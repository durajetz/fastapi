from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.middleware.request_logging import log_requests
from app.core.logger_config import setup_logging
from app.api.routes.predictions import predictions
from app.core.config import app_configs, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


def create_application() -> FastAPI:
    application = FastAPI(**app_configs, lifespan=lifespan)
    application.add_middleware(CORSMiddleware,
                               allow_origins=settings.CORS_ORIGINS,
                               allow_origin_regex=settings.CORS_ORIGINS_REGEX,
                               allow_credentials=True,
                               allow_methods=["GET", "POST", "PUT",
                                              "PATCH", "DELETE", "OPTIONS"],
                               allow_headers=settings.CORS_HEADERS)
    application.include_router(predictions)
    return application


app = create_application()
app.middleware("http")(log_requests)
