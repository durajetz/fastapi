from pydantic import BaseModel
from typing import Any, List


class PredictionRequest(BaseModel):
    prediction_model_name: str
    image_path: str


class PendingPredictionResponse(BaseModel):
    inference_id: str


class PredictionResponse(BaseModel):
    prediction_model_name: str
    results: List[Any] | str
