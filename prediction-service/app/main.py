from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.exception_handlers import entity_not_found_exception_handler, input_required_exception_handler, validation_exception_handler
from app.domain.exceptions.domain_exceptions import EntityNotFoundException, InputRequiredException
from app.middleware.exception_handling import ExceptionHandlingMiddleware
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
    application.add_middleware(ExceptionHandlingMiddleware)
    application.add_exception_handler(
        EntityNotFoundException, entity_not_found_exception_handler)
    application.add_exception_handler(
        RequestValidationError, validation_exception_handler)
    application.add_exception_handler(
        InputRequiredException, input_required_exception_handler)
    application.include_router(predictions)
    return application


app = create_application()
app.middleware("http")(log_requests)
