from pydantic import BaseModel
from typing import Any


class PredictionRequest(BaseModel):
    prediction_model_name: str
    data: Any


class PredictionResponse(BaseModel):
    id: int = 3
