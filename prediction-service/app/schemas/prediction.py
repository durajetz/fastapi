from pydantic import BaseModel
from typing import List, Optional


class PredictionRequest(BaseModel):
    name: str


class PredictionResponse(BaseModel):
    id: int
