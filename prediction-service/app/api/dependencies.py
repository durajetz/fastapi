from fastapi import Depends
from ..core.config import settings
from ..core.message_queue import MessageQueue
from ..infrastructure.torchserve_client import TorchServeClient
from ..infrastructure.redis_client import RedisClient
from ..domain.prediction_service import PredictionService


def get_message_queue() -> MessageQueue:
    return MessageQueue()


def get_redis_client() -> RedisClient:
    return RedisClient(settings.REDIS_HOST)


def get_torchserve_client() -> TorchServeClient:
    return TorchServeClient(settings.TORCHSERVE_HOST)


def get_prediction_service(
    mq: MessageQueue = Depends(get_message_queue),
    torchserve_client: TorchServeClient = Depends(get_torchserve_client),
    redis_client: RedisClient = Depends(get_redis_client)
) -> PredictionService:
    return PredictionService(mq, torchserve_client, redis_client)
