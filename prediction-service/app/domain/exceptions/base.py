from fastapi import HTTPException, status

class CustomBaseException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, detail: str | None = None):
        super().__init__(status_code=status_code, detail=detail or "An unexpected error occurred")