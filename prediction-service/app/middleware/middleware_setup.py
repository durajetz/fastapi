from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .exception_handling import ExceptionHandlingMiddleware
from .request_logging import RequestLoggingMiddleware
from ..core.config import settings


def setup_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=settings.CORS_ORIGINS_REGEX,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=settings.CORS_HEADERS,
    )
    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
