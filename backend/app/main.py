"""
shift. Air Quality — Smog Prediction API (FastAPI)
===================================================
Endpoints
---------
GET  /health          — liveness + artifact presence check
POST /forecast        — PM2.5 prediction from raw feature dict
GET  /forecast/auto   — auto-fetch weather, predict (requires PM2.5 lag params)
GET  /forecast/smart  — fully automatic: fetches weather + PM2.5 lags from APIs

Start command:
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

from __future__ import annotations

# Ensure project root is on sys.path so `import smog` works
import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from smog.config import LOC, FORECAST_WEATHER_URL
from smog.open_meteo import get_json
from smog.features import add_time_features, add_wind_dir_encoding
from smog.ingest import hourly_to_daily_weather
from smog.predict import fetch_recent_pm25, compute_pm25_lags

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

_VOLUME_DIR = Path("/data")
_LOCAL_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR = _VOLUME_DIR if _VOLUME_DIR.is_dir() else _LOCAL_DIR

MODEL_PATH = ARTIFACTS_DIR / "bishkek_pm25_catboost.cbm"
FEATURES_PATH = ARTIFACTS_DIR / "feature_columns.json"

logger = logging.getLogger("smog_api")

# ---------------------------------------------------------------------------
# Model state
# ---------------------------------------------------------------------------
_state: Dict[str, Any] = {
    "model": None,
    "feature_columns": None,
    "load_error": None,
}


def _ensure_model_downloaded() -> None:
    model_url = os.environ.get("MODEL_URL", "").strip()
    if MODEL_PATH.exists():
        logger.info("Model file present at %s", MODEL_PATH)
        return
    if not model_url:
        logger.warning("Model not found at %s and MODEL_URL not set", MODEL_PATH)
        return

    logger.info("Downloading model from %s ...", model_url)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with httpx.stream("GET", model_url, follow_redirects=True, timeout=120) as r:
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=1024 * 256):
                    f.write(chunk)
        logger.info("Model downloaded -> %s (%d bytes)", MODEL_PATH, MODEL_PATH.stat().st_size)
    except Exception as exc:
        logger.error("Model download failed: %s", exc)
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()


def _load_artifacts() -> None:
    try:
        from catboost import CatBoostRegressor

        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
        if not FEATURES_PATH.exists():
            raise FileNotFoundError(f"Features not found: {FEATURES_PATH}")

        model = CatBoostRegressor()
        model.load_model(str(MODEL_PATH))

        with open(FEATURES_PATH) as f:
            feature_columns = json.load(f)

        _state["model"] = model
        _state["feature_columns"] = feature_columns
        _state["load_error"] = None
        logger.info("CatBoost loaded (%d features)", len(feature_columns))

    except Exception as exc:
        _state["model"] = None
        _state["feature_columns"] = None
        _state["load_error"] = str(exc)
        logger.warning("Model not loaded: %s", exc)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_model_downloaded()
    _load_artifacts()
    yield


app = FastAPI(
    title="shift. Smog Prediction API",
    description="PM2.5 forecast for Bishkek using CatBoost",
    version="2.0.0",
    lifespan=lifespan,
)

_cors_origins = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ForecastRequest(BaseModel):
    features: Dict[str, float] = Field(
        ..., description="Feature values keyed by name (must match feature_columns.json)."
    )


class ForecastResponse(BaseModel):
    pm25_predicted: float = Field(..., description="Predicted PM2.5 (ug/m3)")
    unit: str = "ug/m3"
    model: str = "bishkek_pm25_catboost"


class ForecastDay(BaseModel):
    date: str
    pm25: float
    status: str


class MultiForecastResponse(BaseModel):
    city: str = "Bishkek"
    days: int
    forecast: List[ForecastDay]


class HealthResponse(BaseModel):
    ok: bool
    model_loaded: bool
    artifacts_present: bool
    features_count: Optional[int] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _pm_status(pm: float) -> str:
    if pm >= 75:
        return "DANGEROUS"
    if pm >= 35:
        return "MODERATE"
    if pm >= 15:
        return "LIGHT"
    return "CLEAN"


def _require_model():
    if _state["model"] is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded: {_state['load_error']}",
        )
    return _state["model"], _state["feature_columns"]


def _fetch_forecast_daily(days: int) -> pd.DataFrame:
    """Fetch hourly weather forecast and aggregate to daily."""
    params = {
        "latitude": LOC.latitude,
        "longitude": LOC.longitude,
        "timezone": LOC.timezone,
        "forecast_days": max(1, min(16, days)),
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "rain",
            "snowfall",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ]),
    }
    js = get_json(FORECAST_WEATHER_URL, params=params)
    df_hourly = pd.DataFrame(js["hourly"])
    df_hourly["time"] = pd.to_datetime(df_hourly["time"])
    w_d = hourly_to_daily_weather(df_hourly)
    w_d["date"] = pd.to_datetime(w_d["date"])
    return w_d.head(days)


def _predict_multi_day(
    model, feature_columns: List[str], w_d: pd.DataFrame,
    lag1: float, lag2: float, lag7: float,
    roll3: float, roll7: float, roll14: float,
) -> List[Dict[str, Any]]:
    """Run day-by-day prediction with iterative lag updates."""
    results: List[Dict[str, Any]] = []

    for _, row in w_d.iterrows():
        tmp = pd.DataFrame([{"date": pd.to_datetime(row["date"])}])
        tmp = add_time_features(tmp)

        # Inject weather columns
        for c in row.index:
            if c != "date":
                tmp[c] = row[c]

        tmp = add_wind_dir_encoding(tmp)

        # Inject lag features
        tmp["pm25_lag1"] = lag1
        tmp["pm25_lag2"] = lag2
        tmp["pm25_lag7"] = lag7
        tmp["pm25_roll3"] = roll3
        tmp["pm25_roll7"] = roll7
        tmp["pm25_roll14"] = roll14

        # Align to training feature order
        for col in feature_columns:
            if col not in tmp.columns:
                tmp[col] = 0.0

        X = tmp[feature_columns]
        pred = float(model.predict(X)[0])
        pred = max(pred, 0.0)

        results.append({
            "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
            "pm25": round(pred, 1),
            "status": _pm_status(pred),
        })

        # Update lags for next forecast day
        lag2 = lag1
        lag1 = pred
        roll3 = float(np.mean([roll3, pred]))
        roll7 = float(np.mean([roll7, pred]))
        roll14 = float(np.mean([roll14, pred]))

    return results


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    """Liveness + readiness check."""
    artifacts_present = MODEL_PATH.exists() and FEATURES_PATH.exists()
    model_loaded = _state["model"] is not None
    error = _state["load_error"]

    if not artifacts_present and error is None:
        error = f"Missing artifacts at {ARTIFACTS_DIR}"

    return HealthResponse(
        ok=model_loaded,
        model_loaded=model_loaded,
        artifacts_present=artifacts_present,
        features_count=len(_state["feature_columns"]) if _state["feature_columns"] else None,
        error=error,
    )


@app.post("/forecast", response_model=ForecastResponse, tags=["prediction"])
async def forecast(body: ForecastRequest) -> ForecastResponse:
    """Predict PM2.5 from a raw feature vector."""
    model, feature_columns = _require_model()

    row = {col: body.features.get(col, 0.0) for col in feature_columns}
    df = pd.DataFrame([row], columns=feature_columns)

    prediction = float(model.predict(df)[0])
    prediction = round(max(prediction, 0.0), 2)

    return ForecastResponse(pm25_predicted=prediction)


@app.get("/forecast/auto", response_model=MultiForecastResponse, tags=["prediction"])
async def forecast_auto(
    days: int = Query(3, ge=1, le=7, description="Number of forecast days"),
    pm25_lag1: float = Query(..., description="Yesterday PM2.5 (ug/m3)"),
    pm25_lag2: float = Query(..., description="PM2.5 two days ago"),
    pm25_lag7: float = Query(..., description="PM2.5 seven days ago"),
    pm25_roll3: float = Query(..., description="Mean PM2.5 last 3 days"),
    pm25_roll7: float = Query(..., description="Mean PM2.5 last 7 days"),
    pm25_roll14: float = Query(..., description="Mean PM2.5 last 14 days"),
) -> MultiForecastResponse:
    """
    Fetch weather forecast from Open-Meteo, combine with provided PM2.5 lags,
    and predict PM2.5 day-by-day.
    """
    model, feature_columns = _require_model()
    w_d = _fetch_forecast_daily(days)

    results = _predict_multi_day(
        model, feature_columns, w_d,
        lag1=pm25_lag1, lag2=pm25_lag2, lag7=pm25_lag7,
        roll3=pm25_roll3, roll7=pm25_roll7, roll14=pm25_roll14,
    )

    return MultiForecastResponse(days=days, forecast=[ForecastDay(**r) for r in results])


@app.get("/forecast/smart", response_model=MultiForecastResponse, tags=["prediction"])
async def forecast_smart(
    days: int = Query(3, ge=1, le=7, description="Number of forecast days"),
) -> MultiForecastResponse:
    """
    Fully automatic prediction — no manual input needed.
    Fetches both weather forecast AND recent PM2.5 history from Open-Meteo APIs,
    computes lag features automatically, and predicts PM2.5 for the next N days.
    """
    model, feature_columns = _require_model()

    # 1. Fetch weather forecast
    w_d = _fetch_forecast_daily(days)

    # 2. Fetch recent PM2.5 and compute lag features automatically
    pm25_history = fetch_recent_pm25(lookback_days=21)
    lags = compute_pm25_lags(pm25_history)

    results = _predict_multi_day(
        model, feature_columns, w_d,
        lag1=lags["pm25_lag1"], lag2=lags["pm25_lag2"], lag7=lags["pm25_lag7"],
        roll3=lags["pm25_roll3"], roll7=lags["pm25_roll7"], roll14=lags["pm25_roll14"],
    )

    return MultiForecastResponse(days=days, forecast=[ForecastDay(**r) for r in results])
