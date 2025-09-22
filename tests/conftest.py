from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@contextlib.contextmanager
def dep_overrides(**overrides: dict[Callable[..., Any], Callable[..., Any]]):
    from src.core import dependencies as deps

    for key, value in list(overrides.items()):
        if isinstance(key, str):
            overrides[getattr(deps, key)] = overrides.pop(key)

    try:
        for dep, factory in overrides.items():
            app.dependency_overrides[dep] = factory
        yield
    finally:
        for dep in overrides:
            app.dependency_overrides.pop(dep, None)


@pytest.fixture()
def override_deps():
    return dep_overrides
