from datetime import timedelta
from typing import Optional

from fastapi import Depends, Request
from fastapi.responses import Response

from .config import Settings, get_settings
from .errors import AppError


COOKIE_MAX_AGE = int(timedelta(days=7).total_seconds())


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: Optional[str],
    settings: Settings,
) -> None:
    response.set_cookie(
        key=settings.jwt_cookie_name,
        value=access_token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=False,
    )
    if refresh_token:
        response.set_cookie(
            key=settings.refresh_cookie_name,
            value=refresh_token,
            httponly=True,
            max_age=COOKIE_MAX_AGE,
            samesite="lax",
            secure=False,
        )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    response.delete_cookie(settings.jwt_cookie_name)
    response.delete_cookie(settings.refresh_cookie_name)


class AuthContext:
    def __init__(self, access_token: str):
        self.access_token = access_token


async def get_auth_context(request: Request, settings: Settings = Depends(get_settings)) -> AuthContext:
    token = request.cookies.get(settings.jwt_cookie_name)
    if not token:
        raise AppError("Authentication required", code="unauthorized", status_code=401)
    return AuthContext(access_token=token)


__all__ = ["set_auth_cookies", "clear_auth_cookies", "AuthContext", "get_auth_context"]
