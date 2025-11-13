from __future__ import annotations

from typing import Optional

from app.core.errors import AppError
from app.db.supabase_client import SupabaseClient
from app.models.auth import AuthResponse, AuthUser


class AuthService:
    def __init__(self, supabase: SupabaseClient):
        self._supabase = supabase

    async def sign_in(self, email: str, password: str) -> AuthResponse:
        payload = await self._supabase.auth_sign_in(email=email, password=password)
        return AuthResponse.model_validate(payload)

    async def refresh(self, refresh_token: str) -> AuthResponse:
        if not refresh_token:
            raise AppError("Missing refresh token", code="unauthorized", status_code=401)
        payload = await self._supabase.auth_refresh(refresh_token)
        return AuthResponse.model_validate(payload)

    async def me(self, access_token: str) -> AuthUser:
        if not access_token:
            raise AppError("Missing access token", code="unauthorized", status_code=401)
        payload = await self._supabase.auth_get_user(access_token)
        user = payload.get("user") or payload
        return AuthUser.model_validate(user)

    async def sign_out(self, access_token: Optional[str]) -> None:
        if not access_token:
            return
        await self._supabase.auth_sign_out(access_token)


__all__ = ["AuthService"]
