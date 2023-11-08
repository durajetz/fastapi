from typing import Any, Dict, Union
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..dependencies import get_prediction_service
from ...domain.exceptions.domain_exceptions import InputRequiredException
from ...domain.prediction_service import PredictionService
from ...schemas.prediction import PendingPredictionResponse, PredictionRequest, PredictionResponse

predictions = APIRouter()

prediction_responses: Dict[Union[int, str], Dict[str, Any]] = {
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


@predictions.post('/publish-prediction', response_model=PendingPredictionResponse)
async def make_prediction(
    prediction_request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
) -> PendingPredictionResponse:
    """
    Make incoming prediction requests to the requested model.
    """
    if not prediction_request.prediction_model_name:
        raise InputRequiredException(field_name="prediction_model_name")
    inference_id = await prediction_service.publish_prediction(prediction_request)
    return PendingPredictionResponse(inference_id=inference_id)


@predictions.post('/get-result', response_model=PredictionResponse, responses=prediction_responses)
async def get_result(
    inference_id: str,
    prediction_service: PredictionService = Depends(get_prediction_service)
) -> PredictionResponse | StreamingResponse:
    """
    Retrieve the result of a prediction task by task_id.
    """
    result = prediction_service.get_response_from_inference_id(inference_id)
    # if result is None:
    #     return {"detail": "Task not found or not yet completed.", "status": "pending"}
    return result
