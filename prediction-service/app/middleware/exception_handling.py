from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.domain.exceptions.domain_exceptions import CustomBaseException


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except CustomBaseException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "status_code": exc.status_code},
            )
        except Exception as exc:

            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "status_code": 500},
            )
