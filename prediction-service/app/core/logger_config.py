import logging
from loguru import logger
from .intercept_handler import InterceptHandler
from ..core.config import settings


def setup_logging():
    log_path = "logs/prediction_service_{time}.log"
    rotation = "1 week"
    retention = "1 month"
    level = settings.LOG_LEVEL
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    logger.add(
        log_path,
        rotation=rotation,
        retention=retention,
        enqueue=True,
        level=level,
        format=logger_format,
    )

    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]
    logging.getLogger("gunicorn.error").handlers = [InterceptHandler()]
