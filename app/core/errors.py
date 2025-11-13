import uuid
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, detail: str, code: str = "internal_error", status_code: int = 500):
        super().__init__(detail)
        self.detail = detail
        self.code = code
        self.status_code = status_code


def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    payload: Dict[str, Any] = {
        "detail": exc.detail,
        "code": exc.code,
        "request_id": request_id,
    }
    return JSONResponse(status_code=exc.status_code, content=payload)


def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    payload = {
        "detail": "Unexpected error",
        "code": "internal_error",
        "request_id": request_id,
    }
    return JSONResponse(status_code=500, content=payload)


__all__ = ["AppError", "app_error_handler", "unhandled_error_handler"]
