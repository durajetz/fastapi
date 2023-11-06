import json

from loguru import logger


from app.domain.exceptions.domain_exceptions import ServerException
from app.core.message_queue import MessageQueue
from app.infrastructure.torchserve_client import TorchServeClient
from app.schemas.prediction import PredictionRequest, PredictionResponse


class PredictionService:
    def __init__(self, mq: MessageQueue, torchserve_client: TorchServeClient):
        self.mq = mq
        self.torchserve_client = torchserve_client

    async def make_prediction(self, request: PredictionRequest) -> PredictionResponse:
        # Serialize request to JSON and publish to RabbitMQ
        self.mq.publish(json.dumps(request.dict()))

        # Logic to wait for response or timeout to be implemented

        # Direct call to TorchServe for now
        response = await self.torchserve_client.make_prediction(request.prediction_model_name, request.data)

        logger.info(
            f"Prediction output for model {request.prediction_model_name}: {response.json()}")
        return PredictionResponse(prediction_model_name=request.prediction_model_name,
                                  results=response.json())
