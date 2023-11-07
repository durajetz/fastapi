from typing import Any, Dict, Union
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..dependencies import get_prediction_service
from ...domain.exceptions.domain_exceptions import InputRequiredException
from ...domain.prediction_service import PredictionService
from ...schemas.prediction import PredictionRequest, PredictionResponse

predictions = APIRouter()

responses: Dict[Union[int, str], Dict[str, Any]] = {
    200: {
        "description": "A successful response will be either a JSON object with the prediction results or a binary file (such as an image or audio file). The content type of the response will indicate the type of the response.",
        "content": {
            "application/json": {
                "example": {
                    "prediction_model_name": "example_model",
                    "results": [{"label": "cat", "score": 0.9}],
                }
            },
            "image/png": {
                "description": "The result is an image. The image will be returned as a binary file."
            },
            "image/jpeg": {
                "description": "The result is an image. The image will be returned as a binary file."
            },
            "application/octet-stream": {
                "description": "The result is a binary file of an unspecified type."
            }
        }
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
) -> PredictionResponse | StreamingResponse:
    """
    Make incoming prediction requests to the requested model.
    """
    if not prediction_request.prediction_model_name:
        raise InputRequiredException(field_name="prediction_model_name")
    return await prediction_service.make_prediction(prediction_request)
