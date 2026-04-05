from __future__ import annotations
import time
from typing import Any, Dict, Optional
import requests

class OpenMeteoError(RuntimeError):
    pass

def get_json(url: str, params: Dict[str, Any], timeout: int = 30, retries: int = 3, backoff: float = 1.5) -> Dict[str, Any]:
    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code != 200:
                raise OpenMeteoError(f"HTTP {r.status_code}: {r.text[:300]}")
            data = r.json()
            if isinstance(data, dict) and data.get("error"):
                raise OpenMeteoError(f"API error: {data.get('reason')}")
            return data
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff ** attempt)
            else:
                raise OpenMeteoError(f"Failed GET {url} after {retries} retries. Last error: {e}") from e
    raise OpenMeteoError(str(last_err))
