from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Location:
    name: str = "Bishkek"
    latitude: float = 42.87
    longitude: float = 74.59
    timezone: str = "Asia/Bishkek"

@dataclass(frozen=True)
class Paths:
    root: Path = Path(__file__).resolve().parents[1]
    data_processed: Path = root / "data" / "processed"
    artifacts: Path = root / "artifacts"

LOC = Location()
PATHS = Paths()

ARCHIVE_WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
FORECAST_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
