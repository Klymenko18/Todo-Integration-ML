from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast


def _get_model() -> Any:
    import importlib

    joblib = importlib.import_module("joblib")
    return joblib.load("artifacts/model.joblib")


def predict(features: Sequence[float]) -> float:
    model: Any = _get_model()
    y_pred: Any = model.predict([list(features)])
    return float(cast(Sequence[float], y_pred)[0])
