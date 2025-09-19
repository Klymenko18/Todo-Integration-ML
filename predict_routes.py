from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ml_infer import predict_priority

router = APIRouter(prefix="", tags=["Predict"])


class PredictRequest(BaseModel):
    task_description: str = Field(..., min_length=1, max_length=10_000)


class PredictResponse(BaseModel):
    priority: str


@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK)
def predict(req: PredictRequest) -> PredictResponse:
    try:
        pr = predict_priority(req.task_description)
        return PredictResponse(priority=pr)
    except FileNotFoundError as _err:
        # Hide internal traceback source, keep clean client error.
        raise HTTPException(
            status_code=503, detail="Model is not available. Train it first."
        ) from None
