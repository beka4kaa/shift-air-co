from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import requests
from catboost import CatBoostRegressor
from fastapi import FastAPI, HTTPException, Query

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "bishkek_pm25_catboost.cbm"
FEATS_PATH = ARTIFACTS_DIR / "feature_columns.json"

# Bishkek
LAT = 42.87
LON = 74.59
TZ = "Asia/Bishkek"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

app = FastAPI(title="Bishkek Smog Predictor API", version="1.0")


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


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    d = pd.to_datetime(out["date"])
    out["dow"] = d.dt.dayofweek
    out["month"] = d.dt.month
    out["dayofyear"] = d.dt.dayofyear
    out["doy_sin"] = np.sin(2 * np.pi * out["dayofyear"] / 365.25)
    out["doy_cos"] = np.cos(2 * np.pi * out["dayofyear"] / 365.25)
    out["is_weekend"] = (out["dow"] >= 5).astype(int)
    out["heating_season"] = out["month"].isin([10, 11, 12, 1, 2, 3]).astype(int)
    return out


def add_wind_dir_encoding(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["wind_dir_mean_day", "wind_dir_mean_night"]:
        if col in out.columns:
            rad = np.deg2rad(pd.to_numeric(out[col], errors="coerce").fillna(0))
            out[col + "_sin"] = np.sin(rad)
            out[col + "_cos"] = np.cos(rad)
    return out


def fetch_forecast_hourly(days: int) -> pd.DataFrame:
    params = {
        "latitude": LAT,
        "longitude": LON,
        "timezone": TZ,
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
    r = requests.get(FORECAST_URL, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    h = js["hourly"]
    df = pd.DataFrame(h)
    df["time"] = pd.to_datetime(df["time"])
    return df


def hourly_to_daily_weather_forecast(df_h: pd.DataFrame) -> pd.DataFrame:
    df = df_h.copy()
    df["date"] = df["time"].dt.date
    is_night = (df["time"].dt.hour <= 7) | (df["time"].dt.hour >= 20)

    def agg_block(x: pd.DataFrame, suffix: str) -> pd.DataFrame:
        g = x.groupby("date").agg(
            temp_mean=("temperature_2m", "mean"),
            temp_min=("temperature_2m", "min"),
            temp_max=("temperature_2m", "max"),
            rh_mean=("relative_humidity_2m", "mean"),
            rh_max=("relative_humidity_2m", "max"),
            pressure_mean=("surface_pressure", "mean"),
            wind_mean=("wind_speed_10m", "mean"),
            wind_max=("wind_speed_10m", "max"),
            gust_max=("wind_gusts_10m", "max"),
            wind_dir_mean=("wind_direction_10m", "mean"),
            precip_sum=("precipitation", "sum"),
            rain_sum=("rain", "sum"),
            snowfall_sum=("snowfall", "sum"),
        ).reset_index()
        g = g.rename(columns={c: f"{c}{suffix}" for c in g.columns if c != "date"})
        return g

    day = agg_block(df[~is_night], "_day")
    night = agg_block(df[is_night], "_night")
    out = day.merge(night, on="date", how="outer").sort_values("date")
    out["temp_range_day"] = out["temp_max_day"] - out["temp_min_day"]
    out["temp_range_night"] = out["temp_max_night"] - out["temp_min_night"]
    out["date"] = pd.to_datetime(out["date"])
    return out


def pm_status(pm: float) -> str:
    if pm >= 75:
        return "DANGEROUS"
    if pm >= 35:
        return "MODERATE"
    return "CLEAN"


@app.get("/health")
def health():
    if not ARTIFACTS_OK:
        return {"ok": False, "error": STARTUP_ERROR}
    return {"ok": True}


@app.get("/forecast")
def forecast(
    days: int = Query(3, ge=1, le=7),
    # MVP: pass last values from frontend (later: store in DB and update daily)
    pm25_lag1: float = Query(..., description="Yesterday PM2.5 (µg/m³)"),
    pm25_lag2: float = Query(..., description="PM2.5 two days ago (µg/m³)"),
    pm25_lag7: float = Query(..., description="PM2.5 seven days ago (µg/m³)"),
    pm25_roll3: float = Query(..., description="Mean PM2.5 last 3 days"),
    pm25_roll7: float = Query(..., description="Mean PM2.5 last 7 days"),
    pm25_roll14: float = Query(..., description="Mean PM2.5 last 14 days"),
):
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
            "pm25": round(pred, 1),
            "status": pm_status(pred),
        })

        # update lags for next step (simple)
        lag2 = lag1
        lag1 = pred
        # roll update (MVP approximation)
        roll3 = float(np.mean([roll3, pred]))
        roll7 = float(np.mean([roll7, pred]))
        roll14 = float(np.mean([roll14, pred]))

    return {"city": "Bishkek", "days": days, "forecast": results}
