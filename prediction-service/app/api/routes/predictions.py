from typing import Any, Dict, Union
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..dependencies import get_prediction_service
from ...domain.exceptions.domain_exceptions import InputRequiredException
from ...domain.prediction_service import PredictionService
from ...schemas.prediction import (
    PendingPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)

predictions = APIRouter()

prediction_responses: Dict[Union[int, str], Dict[str, Any]] = {
    200: {
        "description": "A successful response will be either a JSON object with the prediction results or a binary file (such as an image or audio file). The content type of the response will indicate the type of the response.",
        "content": {
            "application/json": {
                "examples": {
                    "pendingExample": {
                        "summary": "Pending Result",
                        "value": {
                            "prediction_model_name": "example_model",
                            "results": "Pending",
                        },
                    },
                    "successExample": {
                        "summary": "Successful Prediction",
                        "value": {
                            "prediction_model_name": "example_model",
                            "results": [{"label": "cat", "score": 0.9}],
                        },
                    },
                    "errorExample": {
                        "summary": "Error Prediction",
                        "value": {
                            "prediction_model_name": "example_model",
                            "results": "Error while making the prediction.",
                        },
                    },
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
            },
        },
    },
    422: {
        "description": "Validation Error",
        "content": {"application/json": {"example": {"detail": "field '' required"}}},
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal server error occurred while making a prediction."
                },
            }
        },
    },
}

publish_prediction_responses: Dict[Union[int, str], Dict[str, Any]] = {
    200: {
        "description": "A successful response will be either a JSON object with the prediction results or a binary file (such as an image or audio file). The content type of the response will indicate the type of the response.",
        "content": {
            "application/json": {
                "examples": {
                    "successExample": {
                        "summary": "Successful Prediction",
                        "value": {
                            "inference_id": "example_id",
                        },
                    },
                }
            }
        },
    },
    422: {
        "description": "Validation Error",
        "content": {"application/json": {"example": {"detail": "field '' required"}}},
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal server error occurred while publishing a prediction request."
                },
            }
        },
    },
}


@predictions.post(
    "",
    response_model=PendingPredictionResponse,
    responses=publish_prediction_responses,
)
async def make_prediction(
    prediction_request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> PendingPredictionResponse:
    """
    Make incoming prediction requests to the requested model.
    """
    if not prediction_request.prediction_model_name:
        raise InputRequiredException(field_name="prediction_model_name")
    inference_id = await prediction_service.publish_prediction(prediction_request)
    return PendingPredictionResponse(inference_id=inference_id)


@predictions.get(
    "/{inference_id}", response_model=PredictionResponse, responses=prediction_responses
)
async def get_result(
    inference_id: str,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse | StreamingResponse:
    """
    Retrieve the result of a prediction task by task_id.
    """
    if not inference_id:
        raise InputRequiredException(field_name="inference_id")
    result = prediction_service.get_response_from_inference_id(inference_id)
    return result
