from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from ..domain.exceptions.domain_exceptions import EntityNotFoundException, InputRequiredException, ServerException


def create_error_response(status_code: int, detail: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "status_code": status_code
        },
    )


async def entity_not_found_exception_handler(request: Request, exc: EntityNotFoundException):
    return create_error_response(status.HTTP_404_NOT_FOUND, exc.detail)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = [e['msg'] for e in exc.errors()]
    detail_message = ', '.join(messages)
    return create_error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, detail_message)


async def input_required_exception_handler(request: Request, exc: InputRequiredException):
    return create_error_response(status.HTTP_400_BAD_REQUEST, exc.detail)


async def server_exception_handler(request: Request, exc: ServerException):
    return create_error_response(exc.status_code, exc.detail)
