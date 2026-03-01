"""
shift. Air Quality — Smog Prediction API (FastAPI)
===================================================
Endpoints
---------
GET  /health    — liveness + artifact presence check
POST /forecast  — PM2.5 prediction for Bishkek using CatBoost

Start command (Railway):
    uvicorn app.main:app --host 0.0.0.0 --port $PORT

Artifact paths (relative to backend/ root, i.e. where uvicorn is run):
    artifacts/bishkek_pm25_catboost.cbm
    artifacts/feature_columns.json
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Paths
# Railway: mount a Volume at /data and set MODEL_URL env var.
# Local dev: artifacts live in backend/artifacts/
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../backend/

_VOLUME_DIR = Path("/data")
_LOCAL_DIR = BASE_DIR / "artifacts"
# Prefer /data if it exists (Railway Volume), otherwise fall back to local
ARTIFACTS_DIR = _VOLUME_DIR if _VOLUME_DIR.is_dir() else _LOCAL_DIR

MODEL_PATH = ARTIFACTS_DIR / "bishkek_pm25_catboost.cbm"
FEATURES_PATH = ARTIFACTS_DIR / "feature_columns.json"

logger = logging.getLogger("smog_api")

# ---------------------------------------------------------------------------
# Model state — loaded once at startup
# ---------------------------------------------------------------------------
_state: dict[str, Any] = {
    "model": None,
    "feature_columns": None,
    "load_error": None,
}


def _ensure_model_downloaded() -> None:
    """
    If MODEL_PATH does not exist, download the model from MODEL_URL env var.
    Skipped silently when MODEL_URL is not set (local dev without model).
    """
    model_url = os.environ.get("MODEL_URL", "").strip()
    if MODEL_PATH.exists():
        logger.info("✅ Model file already present at %s", MODEL_PATH)
        return
    if not model_url:
        logger.warning(
            "⚠️  Model not found at %s and MODEL_URL is not set — skipping download",
            MODEL_PATH,
        )
        return

    logger.info("⬇️  Downloading model from %s ...", model_url)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with httpx.stream("GET", model_url, follow_redirects=True, timeout=120) as r:
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=1024 * 256):
                    f.write(chunk)
        logger.info("✅ Model downloaded → %s (%d bytes)", MODEL_PATH, MODEL_PATH.stat().st_size)
    except Exception as exc:  # noqa: BLE001
        # Don't crash the server — /health will report the missing model
        logger.error("❌ Model download failed: %s", exc)
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()  # remove partial file


def _load_artifacts() -> None:
    """Try to load CatBoost model and feature columns. Store errors gracefully."""
    try:
        from catboost import CatBoostRegressor  # type: ignore

        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        if not FEATURES_PATH.exists():
            raise FileNotFoundError(f"Feature columns file not found: {FEATURES_PATH}")

        model = CatBoostRegressor()
        model.load_model(str(MODEL_PATH))

        with open(FEATURES_PATH) as f:
            feature_columns = json.load(f)

        _state["model"] = model
        _state["feature_columns"] = feature_columns
        _state["load_error"] = None
        logger.info("✅ CatBoost model loaded successfully (%d features)", len(feature_columns))

    except Exception as exc:  # noqa: BLE001
        _state["model"] = None
        _state["feature_columns"] = None
        _state["load_error"] = str(exc)
        logger.warning("⚠️  Model not loaded: %s", exc)


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_model_downloaded()  # download from MODEL_URL if not on Volume
    _load_artifacts()
    yield
    # cleanup (nothing to do for catboost)


app = FastAPI(
    title="shift. Smog Prediction API",
    description="PM2.5 forecast for Bishkek using CatBoost",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — restrict in production via CORS_ALLOWED_ORIGINS env var
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
    """
    Send the feature values as a flat dict matching feature_columns.json.

    Example with typical time + weather features:
    {
        "features": {
            "hour": 14,
            "day_of_week": 2,
            "month": 6,
            "temperature": 28.5,
            "humidity": 45.0,
            "wind_speed": 3.2,
            "pressure": 1013.0
        }
    }
    """

    features: dict[str, float] = Field(
        ...,
        description="Feature values keyed by name (must match feature_columns.json).",
    )


class ForecastResponse(BaseModel):
    pm25_predicted: float = Field(..., description="Predicted PM2.5 concentration (µg/m³)")
    unit: str = "µg/m³"
    model: str = "bishkek_pm25_catboost"


class HealthResponse(BaseModel):
    ok: bool
    model_loaded: bool
    artifacts_present: bool
    error: str | None = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    """
    Liveness + readiness check.
    Returns ok=true only when both artifact files exist and the model is loaded.
    """
    artifacts_present = MODEL_PATH.exists() and FEATURES_PATH.exists()
    model_loaded = _state["model"] is not None
    error = _state["load_error"]

    if not artifacts_present and error is None:
        error = (
            f"Missing artifact files. Expected:\n"
            f"  {MODEL_PATH}\n"
            f"  {FEATURES_PATH}"
        )

    return HealthResponse(
        ok=model_loaded,
        model_loaded=model_loaded,
        artifacts_present=artifacts_present,
        error=error,
    )


@app.post("/forecast", response_model=ForecastResponse, tags=["prediction"])
async def forecast(body: ForecastRequest) -> ForecastResponse:
    """
    Predict PM2.5 for the supplied feature vector.

    All keys in `features` must match the column names in `feature_columns.json`.
    Missing columns are filled with 0; extra keys are silently ignored.
    """
    if _state["model"] is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded: {_state['load_error']}",
        )

    feature_columns: list[str] = _state["feature_columns"]
    model = _state["model"]

    # Build a single-row DataFrame aligned to training columns
    row = {col: body.features.get(col, 0.0) for col in feature_columns}
    df = pd.DataFrame([row], columns=feature_columns)

    prediction: float = float(model.predict(df)[0])
    prediction = round(max(prediction, 0.0), 2)  # PM2.5 cannot be negative

    return ForecastResponse(pm25_predicted=prediction)
