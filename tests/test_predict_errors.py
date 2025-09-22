from __future__ import annotations

from fastapi import status


def test_predict_503_when_model_missing(client, monkeypatch):
    import src.api.v1.predict_routes as pr

    def _raise(_):
        raise FileNotFoundError("no model")

    monkeypatch.setattr(pr, "predict_priority", _raise)
    r = client.post("/predict", json={"description": "text"})
    assert r.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
