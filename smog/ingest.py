from __future__ import annotations
from datetime import date
import pandas as pd
from .config import LOC, PATHS, ARCHIVE_WEATHER_URL, AIR_QUALITY_URL
from .open_meteo import get_json

def fetch_hourly_weather(start: str, end: str) -> pd.DataFrame:
    params = {
        "latitude": LOC.latitude,
        "longitude": LOC.longitude,
        "start_date": start,
        "end_date": end,
        "timezone": LOC.timezone,
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
    js = get_json(ARCHIVE_WEATHER_URL, params=params)
    df = pd.DataFrame(js["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df

def fetch_hourly_pm25(start: str, end: str) -> pd.DataFrame:
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
    return df

def hourly_to_daily_weather(df_h: pd.DataFrame) -> pd.DataFrame:
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
    return out

def hourly_to_daily_pm25(df_h: pd.DataFrame) -> pd.DataFrame:
    df = df_h.copy()
    df["date"] = df["time"].dt.date
    return df.groupby("date").agg(
        pm25_mean=("pm2_5", "mean"),
        pm25_max=("pm2_5", "max"),
    ).reset_index()

def build_daily_dataset(start: str, end: str) -> pd.DataFrame:
    w_d = hourly_to_daily_weather(fetch_hourly_weather(start, end))
    a_d = hourly_to_daily_pm25(fetch_hourly_pm25(start, end))
    df = w_d.merge(a_d, on="date", how="inner").sort_values("date")
    df["date"] = pd.to_datetime(df["date"])
    return df

def run_ingest(start="2022-08-01", end=None):
    if end is None:
        end = str(date.today())
    df = build_daily_dataset(start, end)
    PATHS.data_processed.mkdir(parents=True, exist_ok=True)
    out = PATHS.data_processed / "bishkek_daily.parquet"
    df.to_parquet(out, index=False)
    return out, df
