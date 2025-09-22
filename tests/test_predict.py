from __future__ import annotations

from fastapi import status


def test_train_sync_and_predict(client, monkeypatch):
    import src.api.v1.predict_routes as pr

    def fake_train_from_csv(path: str):
        return ("any/model.joblib", 1.0)

    monkeypatch.setattr(pr, "train_from_csv", fake_train_from_csv)

    r = client.post("/predict/train-sync", json={"csv_path": "/app/data/tasks.csv"})
    assert r.status_code == status.HTTP_200_OK, r.text
    data = r.json()
    assert "model_path" in data and isinstance(data["model_path"], str)
    assert data["train_acc"] == 1.0

    def fake_predict_priority(desc: str):
        return ("high", 0.6)

    monkeypatch.setattr(pr, "predict_priority", fake_predict_priority)

    rr = client.post("/predict", json={"description": "Fix login bug"})
    assert rr.status_code == status.HTTP_200_OK
    out = rr.json()
    assert out["priority"] == "high" and 0.0 <= out["prob_high"] <= 1.0


def test_predict_model_missing(client, monkeypatch):
    import src.api.v1.predict_routes as pr

    def raise_not_found(desc: str):
        raise FileNotFoundError("Model file not found")

    monkeypatch.setattr(pr, "predict_priority", raise_not_found)

    rr = client.post("/predict", json={"description": "whatever"})
    assert rr.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_train_async_returns_task_id(client, monkeypatch):
    import src.api.v1.predict_routes as pr

    class DummyRes:
        id = "task-123"

    class DummyTask:
        def delay(self, csv_path: str):
            return DummyRes()

    monkeypatch.setattr(pr, "train_model_from_csv", DummyTask())

    r = client.post("/predict/train", json={"csv_path": "/x.csv"})
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["task_id"] == "task-123"
