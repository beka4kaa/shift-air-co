from __future__ import annotations
import numpy as np
import pandas as pd

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    d = out["date"]
    out["dow"] = d.dt.dayofweek
    out["month"] = d.dt.month
    out["dayofyear"] = d.dt.dayofyear
    out["doy_sin"] = np.sin(2 * np.pi * out["dayofyear"] / 365.25)
    out["doy_cos"] = np.cos(2 * np.pi * out["dayofyear"] / 365.25)
    out["is_weekend"] = (out["dow"] >= 5).astype(int)
    out["heating_season"] = out["month"].isin([10,11,12,1,2,3]).astype(int)
    return out

def add_pm_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pm25_lag1"] = out["pm25_mean"].shift(1)
    out["pm25_lag2"] = out["pm25_mean"].shift(2)
    out["pm25_lag7"] = out["pm25_mean"].shift(7)
    out["pm25_roll3"] = out["pm25_mean"].shift(1).rolling(3).mean()
    out["pm25_roll7"] = out["pm25_mean"].shift(1).rolling(7).mean()
    out["pm25_roll14"] = out["pm25_mean"].shift(1).rolling(14).mean()
    return out

def add_wind_dir_encoding(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["wind_dir_mean_day", "wind_dir_mean_night"]:
        if col in out.columns:
            rad = np.deg2rad(out[col].fillna(0))
            out[col + "_sin"] = np.sin(rad)
            out[col + "_cos"] = np.cos(rad)
    return out

def make_training_frame(df_daily: pd.DataFrame) -> pd.DataFrame:
    df = df_daily.copy().sort_values("date").reset_index(drop=True)
    df = add_time_features(df)
    df = add_pm_lag_features(df)
    df = add_wind_dir_encoding(df)
    return df

def _unique(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def get_feature_columns(df: pd.DataFrame) -> list[str]:
    weather_cols = [
        "temp_mean_day","temp_min_day","temp_max_day","rh_mean_day","rh_max_day",
        "pressure_mean_day","wind_mean_day","wind_max_day","gust_max_day",
        "precip_sum_day","rain_sum_day","snowfall_sum_day","temp_range_day",
        "temp_mean_night","temp_min_night","temp_max_night","rh_mean_night","rh_max_night",
        "pressure_mean_night","wind_mean_night","wind_max_night","gust_max_night",
        "precip_sum_night","rain_sum_night","snowfall_sum_night","temp_range_night",
    ]
    wind_dir_cols = [c for c in df.columns if c.startswith("wind_dir_mean_") and (c.endswith("_sin") or c.endswith("_cos"))]
    base = [
        "dow","month","doy_sin","doy_cos","is_weekend","heating_season",
        "pm25_lag1","pm25_lag2","pm25_lag7","pm25_roll3","pm25_roll7","pm25_roll14",
    ]
    cols = [c for c in base + weather_cols + wind_dir_cols if c in df.columns]
    return _unique(cols)
