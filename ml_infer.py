from functools import lru_cache
from typing import Literal

from joblib import load

from settings import get_settings

__all__ = ["predict_priority"]

_settings = get_settings()


@lru_cache
def _model():
    return load(_settings.model_path)


def predict_priority(text: str) -> Literal["high", "low"]:
    model = _model()
    pred = model.predict([text])[0]
    return "high" if str(pred).lower() == "high" else "low"
