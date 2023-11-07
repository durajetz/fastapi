from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.exception_setup import setup_exception_handlers
from .middleware.middleware_setup import setup_middlewares
from .api.router_setup import router as api_router
from .core.logger_config import setup_logging
from .core.config import app_configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


def create_application() -> FastAPI:
    application = FastAPI(**app_configs, lifespan=lifespan)

    setup_middlewares(application)
    setup_exception_handlers(application)

    application.include_router(api_router)

    return application


app = create_application()
