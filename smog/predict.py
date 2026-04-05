"""
smog.predict — Inference module
================================
Fetches weather forecast (Open-Meteo Forecast API) and recent PM2.5 history
(Open-Meteo Air Quality API), builds the same feature set used during training,
loads the saved CatBoost model, and outputs PM2.5 predictions for the next N days.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from .config import LOC, PATHS, FORECAST_WEATHER_URL, AIR_QUALITY_URL
from .open_meteo import get_json
from .ingest import hourly_to_daily_weather, hourly_to_daily_pm25
from .features import add_time_features, add_wind_dir_encoding


# ---------------------------------------------------------------------------
# 1. Fetch weather forecast (future days)
# ---------------------------------------------------------------------------
def fetch_forecast_weather(days: int = 5) -> pd.DataFrame:
    """Fetch hourly weather forecast from Open-Meteo for `days` ahead."""
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


# ---------------------------------------------------------------------------
# 2. Fetch recent PM2.5 history (for lag features)
# ---------------------------------------------------------------------------
def fetch_recent_pm25(lookback_days: int = 21) -> pd.DataFrame:
    """
    Fetch the last `lookback_days` of hourly PM2.5 from the Air Quality API,
    aggregate to daily means/max.  We need at least 14 days for pm25_roll14.
    """
    end = str(date.today())
    start = str(date.today() - timedelta(days=lookback_days))
    params = {
        "latitude": LOC.latitude,
        "longitude": LOC.longitude,
        "start_date": start,
        "end_date": end,
        "timezone": LOC.timezone,
        "hourly": "pm2_5",
    }
    js = get_json(AIR_QUALITY_URL, params=params)
    df = pd.DataFrame(js["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return hourly_to_daily_pm25(df)


# ---------------------------------------------------------------------------
# 3. Compute lag features from recent PM2.5 history
# ---------------------------------------------------------------------------
def compute_pm25_lags(pm25_daily: pd.DataFrame) -> Dict[str, float]:
    """
    Given a daily PM2.5 DataFrame (columns: date, pm25_mean, pm25_max),
    compute the lag/rolling features needed by the model for the *next* day.

    Returns a dict with keys: pm25_lag1, pm25_lag2, pm25_lag7,
    pm25_roll3, pm25_roll7, pm25_roll14.
    """
    s = pm25_daily.sort_values("date")["pm25_mean"].values.astype(float)

    # Fill NaNs with series mean (safety net)
    s_mean = float(np.nanmean(s)) if len(s) > 0 else 0.0
    s = np.where(np.isnan(s), s_mean, s)

    def safe_get(arr, idx):
        """Get value at negative index (from end), fallback to mean."""
        try:
            return float(arr[idx])
        except IndexError:
            return s_mean

    return {
        "pm25_lag1": safe_get(s, -1),
        "pm25_lag2": safe_get(s, -2),
        "pm25_lag7": safe_get(s, -7),
        "pm25_roll3": float(np.mean(s[-3:])) if len(s) >= 3 else s_mean,
        "pm25_roll7": float(np.mean(s[-7:])) if len(s) >= 7 else s_mean,
        "pm25_roll14": float(np.mean(s[-14:])) if len(s) >= 14 else s_mean,
    }


# ---------------------------------------------------------------------------
# 4. Build prediction DataFrame
# ---------------------------------------------------------------------------
def build_prediction_frame(
    forecast_daily: pd.DataFrame,
    lags: Dict[str, float],
    feature_columns: list[str],
) -> pd.DataFrame:
    """
    For each forecast day, combine weather features + time features +
    lag features into a single row, aligned to `feature_columns`.

    Lag features are updated iteratively: after predicting day N, the
    predicted PM2.5 becomes lag1 for day N+1, etc.
    """
    rows = []
    lag1 = lags["pm25_lag1"]
    lag2 = lags["pm25_lag2"]
    lag7 = lags["pm25_lag7"]
    roll3 = lags["pm25_roll3"]
    roll7 = lags["pm25_roll7"]
    roll14 = lags["pm25_roll14"]

    for _, row in forecast_daily.iterrows():
        tmp = pd.DataFrame([{"date": pd.to_datetime(row["date"])}])
        tmp = add_time_features(tmp)

        # Inject weather columns from forecast
        for c in row.index:
            if c != "date":
                tmp[c] = row[c]

        tmp = add_wind_dir_encoding(tmp)

        # Inject PM2.5 lag features
        tmp["pm25_lag1"] = lag1
        tmp["pm25_lag2"] = lag2
        tmp["pm25_lag7"] = lag7
        tmp["pm25_roll3"] = roll3
        tmp["pm25_roll7"] = roll7
        tmp["pm25_roll14"] = roll14

        rows.append(tmp)

    df = pd.concat(rows, ignore_index=True)
    # Align to training columns, fill missing with 0
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0.0
    return df[feature_columns]


# ---------------------------------------------------------------------------
# 5. PM2.5 → status label
# ---------------------------------------------------------------------------
def pm_status(pm: float) -> str:
    """WHO-inspired AQI status label."""
    if pm >= 75:
        return "🔴 DANGEROUS"
    if pm >= 35:
        return "🟠 MODERATE"
    if pm >= 15:
        return "🟡 LIGHT"
    return "🟢 CLEAN"


# ---------------------------------------------------------------------------
# 6. Main entry point
# ---------------------------------------------------------------------------
def run_predict(days: int = 5) -> List[Dict[str, Any]]:
    """
    End-to-end prediction pipeline:
      1. Load saved model + feature columns
      2. Fetch weather forecast for `days` ahead
      3. Fetch recent PM2.5 history (for lag features)
      4. Build feature matrix & predict day-by-day
      5. Return list of { date, pm25, status }
    """
    # --- Load artifacts ---
    model_path = PATHS.artifacts / "bishkek_pm25_catboost.cbm"
    feats_path = PATHS.artifacts / "feature_columns.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}\n"
            f"Run `python main.py train` first to train the model."
        )
    if not feats_path.exists():
        raise FileNotFoundError(
            f"Feature columns not found: {feats_path}\n"
            f"Run `python main.py train` first."
        )

    model = CatBoostRegressor()
    model.load_model(str(model_path))

    with open(feats_path, encoding="utf-8") as f:
        feature_columns = json.load(f)

    # --- Fetch data ---
    print(f"🌤️  Fetching weather forecast for {days} days …")
    hourly_forecast = fetch_forecast_weather(days=days)
    forecast_daily = hourly_to_daily_weather(hourly_forecast)
    forecast_daily["date"] = pd.to_datetime(forecast_daily["date"])
    # Keep only future days (today + ahead)
    forecast_daily = forecast_daily.head(days)

    print("📊 Fetching recent PM2.5 history (for lag features) …")
    pm25_history = fetch_recent_pm25(lookback_days=21)
    lags = compute_pm25_lags(pm25_history)

    # --- Predict day-by-day (updating lags iteratively) ---
    results: List[Dict[str, Any]] = []
    lag1 = lags["pm25_lag1"]
    lag2 = lags["pm25_lag2"]
    lag7 = lags["pm25_lag7"]
    roll3 = lags["pm25_roll3"]
    roll7 = lags["pm25_roll7"]
    roll14 = lags["pm25_roll14"]

    for _, row in forecast_daily.iterrows():
        current_lags = {
            "pm25_lag1": lag1,
            "pm25_lag2": lag2,
            "pm25_lag7": lag7,
            "pm25_roll3": roll3,
            "pm25_roll7": roll7,
            "pm25_roll14": roll14,
        }

        X = build_prediction_frame(
            pd.DataFrame([row]),
            lags=current_lags,
            feature_columns=feature_columns,
        )

        pred = float(model.predict(X)[0])
        pred = max(pred, 0.0)  # PM2.5 can't be negative

        results.append({
            "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
            "pm25": round(pred, 1),
            "status": pm_status(pred),
        })

        # Update lags for the next forecast day
        lag2 = lag1
        lag1 = pred
        roll3 = float(np.mean([roll3, roll3, pred]))   # approximate
        roll7 = float(np.mean([roll7, roll7, pred]))
        roll14 = float(np.mean([roll14, roll14, pred]))

    return results
