"""
Bishkek Smog Predictor API (FastAPI)
====================================
GET  /health    — liveness + artifact check
GET  /forecast  — multi-day PM2.5 forecast using CatBoost + Open-Meteo weather

Uses the shared `smog` package for feature engineering and Open-Meteo helpers.
"""

from __future__ import annotations

# Ensure project root is on sys.path so `import smog` works when running
# from backend/ai/ directory (e.g. `cd backend/ai && uvicorn app.main:app`)
import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parents[3]  # backend/ai/app/main.py → project root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ── shared smog package ──────────────────────────────────────────────────────
from smog.config import LOC, FORECAST_WEATHER_URL
from smog.open_meteo import get_json
from smog.features import add_time_features, add_wind_dir_encoding

logger = logging.getLogger("smog_ai_api")

# ── Artifact paths ───────────────────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "bishkek_pm25_catboost.cbm"
FEATS_PATH = ARTIFACTS_DIR / "feature_columns.json"

app = FastAPI(title="Bishkek Smog Predictor API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Load model ───────────────────────────────────────────────────────────────
def _load_artifacts():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    if not FEATS_PATH.exists():
        raise FileNotFoundError(f"Features not found: {FEATS_PATH}")

    m = CatBoostRegressor()
    m.load_model(str(MODEL_PATH))
    feature_cols = json.loads(FEATS_PATH.read_text(encoding="utf-8"))
    return m, feature_cols


try:
    model, FEATURE_COLS = _load_artifacts()
    ARTIFACTS_OK = True
    STARTUP_ERROR = ""
except Exception as e:
    model, FEATURE_COLS = None, None
    ARTIFACTS_OK = False
    STARTUP_ERROR = str(e)


# ── Weather forecast (reuses smog.open_meteo) ────────────────────────────────
def fetch_forecast_hourly(days: int) -> pd.DataFrame:
    """Fetch hourly weather forecast from Open-Meteo via shared client."""
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
    df = pd.DataFrame(js["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df


def hourly_to_daily_weather_forecast(df_h: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly forecast → daily (day/night split).

    Uses the same aggregation logic as smog.ingest.hourly_to_daily_weather.
    """
    from smog.ingest import hourly_to_daily_weather
    return hourly_to_daily_weather(df_h)


def pm_status(pm: float) -> str:
    if pm >= 75:
        return "DANGEROUS"
    if pm >= 35:
        return "MODERATE"
    return "CLEAN"


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    if not ARTIFACTS_OK:
        return {"ok": False, "error": STARTUP_ERROR}
    return {"ok": True}


@app.get("/forecast")
def forecast(
    days: int = Query(3, ge=1, le=7),
    pm25_lag1: float = Query(..., description="Yesterday PM2.5 (µg/m³)"),
    pm25_lag2: float = Query(..., description="PM2.5 two days ago (µg/m³)"),
    pm25_lag7: float = Query(..., description="PM2.5 seven days ago (µg/m³)"),
    pm25_roll3: float = Query(..., description="Mean PM2.5 last 3 days"),
    pm25_roll7: float = Query(..., description="Mean PM2.5 last 7 days"),
    pm25_roll14: float = Query(..., description="Mean PM2.5 last 14 days"),
):
    """Multi-day PM2.5 forecast for Bishkek.

    Fetches weather forecast from Open-Meteo, builds features using the
    shared `smog` package, and runs CatBoost predictions day-by-day.
    """
    if not ARTIFACTS_OK or model is None:
        raise HTTPException(status_code=500, detail=f"Artifacts not loaded: {STARTUP_ERROR}")

    w_h = fetch_forecast_hourly(days=days)
    w_d = hourly_to_daily_weather_forecast(w_h).head(days)

    results: List[Dict[str, Any]] = []
    lag1, lag2, lag7 = pm25_lag1, pm25_lag2, pm25_lag7
    roll3, roll7, roll14 = pm25_roll3, pm25_roll7, pm25_roll14

    for _, row in w_d.iterrows():
        tmp = pd.DataFrame([{"date": row["date"]}])
        tmp = add_time_features(tmp)

        tmp["pm25_lag1"] = lag1
        tmp["pm25_lag2"] = lag2
        tmp["pm25_lag7"] = lag7
        tmp["pm25_roll3"] = roll3
        tmp["pm25_roll7"] = roll7
        tmp["pm25_roll14"] = roll14

        for c in row.index:
            if c != "date":
                tmp[c] = row[c]

        tmp = add_wind_dir_encoding(tmp)

        X = tmp[FEATURE_COLS]
        pred = float(model.predict(X)[0])

        results.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "pm25": round(max(pred, 0.0), 1),
            "status": pm_status(pred),
        })

        # update lags for next step
        lag2 = lag1
        lag1 = pred
        roll3 = float(np.mean([roll3, pred]))
        roll7 = float(np.mean([roll7, pred]))
        roll14 = float(np.mean([roll14, pred]))

    return {"city": "Bishkek", "days": days, "forecast": results}
