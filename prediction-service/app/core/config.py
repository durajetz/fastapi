import os
from typing import Any
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    SITE_DOMAIN: str = "myapp.com"
    TORCHSERVE_HOST: str = os.getenv('TORCHSERVE_HOST', 'localhost:8080')
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost:6379')
    RABBITMQ_HOST: str = os.getenv(
        'RABBITMQ_URL', 'amqp://user:password@localhost:5672/')
    INCOMING_QUEUE: str = 'prediction_requests'
    RESULT_QUEUE: str = 'prediction_results'
    LOG_LEVEL: str = 'INFO'
    CORS_ORIGINS: list[str] = ["http://localhost",
                               "http://localhost:8080"]
    CORS_ORIGINS_REGEX: str | None = "http://localhost*"
    CORS_HEADERS: list[str] = ["*"]
    RATE_LIMITER_MAX_TOKENS: int = 10
    RATE_LIMITER_REFILL_TIME: int = 1
    PREDICTION_TIMEOUT: int = int(os.getenv('PREDICTION_TIMEOUT', '60'))


settings = Config()

app_configs: dict[str, Any] = {"title": "Predictions API"}
app_configs["openapi_url"] = f"/api/predictions/openapi.json"
app_configs["docs_url"] = f"/api/predictions/docs"
