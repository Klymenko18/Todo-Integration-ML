import time
from typing import Any

import httpx

from settings import get_settings

_settings = get_settings()


def fetch_json(url: str) -> list[dict[str, Any]]:
    """HTTP GET with timeouts & simple retry backoff."""
    timeout = _settings.http_timeout
    max_retries = _settings.http_max_retries
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(url)
                resp.raise_for_status()
                data = resp.json()
                if not isinstance(data, list):
                    raise ValueError("Expected JSON array")
                return data  # type: ignore[return-value]
        except Exception as exc:
            last_exc = exc
            if attempt == max_retries:
                raise
            time.sleep(min(2**attempt, 8))
    assert last_exc
    raise last_exc
