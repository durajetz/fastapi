from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.core.exception_handlers import (
    entity_not_found_exception_handler,
    input_required_exception_handler,
    server_exception_handler,
    validation_exception_handler,
)
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundException,
    InputRequiredException,
    ServerException,
)


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(EntityNotFoundException,
                              entity_not_found_exception_handler)
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)
    app.add_exception_handler(InputRequiredException,
                              input_required_exception_handler)
    app.add_exception_handler(ServerException, server_exception_handler)
