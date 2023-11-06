from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from app.infrastructure.torchserve_client import TorchServeClient
from app.api.dependencies import get_message_queue, get_prediction_service, get_torchserve_client
from app.domain.prediction_service import PredictionService
from app.core.message_queue import MessageQueue
from app.core.config import settings
from app.schemas.prediction import PredictionRequest, PredictionResponse

predictions = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


@predictions.post('/make-prediction', response_model=PredictionResponse)
async def make_prediction(
    prediction_request: PredictionRequest,
    torchserve_client: TorchServeClient = Depends(get_torchserve_client),
    mq: MessageQueue = Depends(get_message_queue) 
):
    """
    Make incoming prediction requests to the requested model.
    """
    prediction_service = PredictionService(mq, torchserve_client)
    return await prediction_service.make_prediction(prediction_request)
