from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


class HttpClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout)

    def get_json(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._client.close()


def fetch_json(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    timeout: float = 10.0,
) -> Any:
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
