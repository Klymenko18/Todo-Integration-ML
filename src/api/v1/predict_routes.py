from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.ml_infer import MODEL_PATH, predict_priority, train_from_csv
from src.workers.tasks.task_train_model import train_model_from_csv

router = APIRouter(prefix="/predict", tags=["ML"])


class PredictIn(BaseModel):
    description: str = Field(..., min_length=1)


class PredictOut(BaseModel):
    priority: str
    prob_high: float


@router.post("", response_model=PredictOut)
def predict(payload: PredictIn) -> PredictOut:
    try:
        label, p_high = predict_priority(payload.description)
        priority = "high" if label.lower().strip() == "high" else "low"
        return PredictOut(priority=priority, prob_high=p_high)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"prediction_failed: {e}")


class TrainIn(BaseModel):
    csv_path: str = Field("/app/data/tasks.csv")


class TrainOut(BaseModel):
    task_id: str


@router.post("/train", response_model=TrainOut)
def train(payload: TrainIn) -> TrainOut:
    task = train_model_from_csv.delay(payload.csv_path)
    return TrainOut(task_id=task.id)


class TrainSyncOut(BaseModel):
    model_path: str
    train_acc: float


@router.post("/train-sync", response_model=TrainSyncOut)
def train_sync(payload: TrainIn) -> TrainSyncOut:
    try:
        _, acc = train_from_csv(payload.csv_path)
        return TrainSyncOut(model_path=str(MODEL_PATH), train_acc=acc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
