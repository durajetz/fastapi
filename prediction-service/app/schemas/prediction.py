from pydantic import BaseModel
from typing import Any, List


class PredictionRequest(BaseModel):
    prediction_model_name: str
    data: Any


class PredictionResponse(BaseModel):
    prediction_model_name: str
    results: List[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "prediction_model_name": "example_model",
                "results": [
                    {"label": "cat", "score": 0.9},
                ],
            }
        }
