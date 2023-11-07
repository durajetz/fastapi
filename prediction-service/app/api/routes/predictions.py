from typing import Any, Dict, Union
from fastapi import APIRouter, Depends
from ...domain.exceptions.domain_exceptions import InputRequiredException
from ...domain.prediction_service import PredictionService
from ..dependencies import get_prediction_service
from ...schemas.prediction import PredictionRequest, PredictionResponse

predictions = APIRouter()

responses: Dict[Union[int, str], Dict[str, Any]] = {
    200: {
        "description": "Successful Response",
        "model": PredictionResponse,
    },
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "field '' required"
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error occurred while making a prediction."},
            }
        }
    },
}


@predictions.post('/make-prediction', response_model=PredictionResponse, responses=responses)
async def make_prediction(
    prediction_request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Make incoming prediction requests to the requested model.
    """
    if not prediction_request.prediction_model_name:
        raise InputRequiredException(field_name="prediction_model_name")
    return await prediction_service.make_prediction(prediction_request)
