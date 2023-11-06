from .base import CustomBaseException
from fastapi import status


class EntityNotFoundException(CustomBaseException):
    def __init__(self, detail: str = "Entity not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ServerException(CustomBaseException):
    def __init__(self, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, detail: str = "Server error"):
        super().__init__(status_code=status_code, detail=detail)


class InputRequiredException(CustomBaseException):
    def __init__(self, field_name: str, detail: str | None = None):
        detail = detail if detail is not None else f"The '{field_name}' field is required."
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
