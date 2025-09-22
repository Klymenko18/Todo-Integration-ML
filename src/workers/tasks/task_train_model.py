from __future__ import annotations

from src.core.celery_app import celery_app
from src.ml_infer import MODEL_PATH, train_from_csv


@celery_app.task(name="ml.train_model_from_csv")
def train_model_from_csv(csv_path: str) -> dict[str, str]:
    _, acc = train_from_csv(csv_path)
    return {"model_path": str(MODEL_PATH), "train_acc": f"{acc:.6f}"}
