from fastapi import FastAPI
from app.api.predictions import predictions
from app.core.config import app_configs, settings


def create_application() -> FastAPI:
    application = FastAPI(**app_configs)
    application.include_router(predictions)
    return application


app = create_application()
