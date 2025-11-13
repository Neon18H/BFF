from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.core.errors import AppError


@dataclass
class SupabaseResponse:
    data: Any
    headers: httpx.Headers


class SupabaseClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        base_url = str(settings.supabase_url).rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=settings.request_timeout,
            headers={"apikey": settings.supabase_anon_key},
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _handle_response(self, response: httpx.Response) -> SupabaseResponse:
        if response.status_code >= 400:
            try:
                payload = response.json()
                message = (
                    payload.get("message")
                    or payload.get("error_description")
                    or payload.get("error")
                )
            except Exception:
                message = None
            raise AppError(
                detail=message or "Supabase request failed",
                code="supabase_error",
                status_code=response.status_code,
            )
        if not response.content:
            data: Any = {}
        else:
            try:
                data = response.json()
            except ValueError:
                data = {}
        return SupabaseResponse(data=data, headers=response.headers)

    async def auth_sign_in(self, email: str, password: str) -> Any:
        response = await self._client.post(
            "/auth/v1/token?grant_type=password",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json", "apikey": self._settings.supabase_anon_key},
        )
        return (await self._handle_response(response)).data

    async def auth_refresh(self, refresh_token: str) -> Any:
        response = await self._client.post(
            "/auth/v1/token?grant_type=refresh_token",
            json={"refresh_token": refresh_token},
            headers={"Content-Type": "application/json", "apikey": self._settings.supabase_anon_key},
        )
        return (await self._handle_response(response)).data

    async def auth_get_user(self, access_token: str) -> Any:
        response = await self._client.get(
            "/auth/v1/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": self._settings.supabase_anon_key,
            },
        )
        return (await self._handle_response(response)).data

    async def auth_sign_out(self, access_token: str) -> None:
        response = await self._client.post(
            "/auth/v1/logout",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": self._settings.supabase_anon_key,
            },
        )
        if response.status_code >= 400:
            await self._handle_response(response)

    async def rest_request(
        self,
        method: str,
        path: str,
        access_token: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> SupabaseResponse:
        final_headers = {
            "Authorization": f"Bearer {access_token}",
            "apikey": self._settings.supabase_anon_key,
            "Content-Type": "application/json",
        }
        if headers:
            final_headers.update(headers)
        response = await self._client.request(
            method,
            f"/rest/v1/{path}",
            params=params,
            json=json,
            headers=final_headers,
        )
        if method.upper() == "DELETE" and response.status_code in (200, 204):
            return SupabaseResponse(data=None, headers=response.headers)
        if response.status_code == 204:
            return SupabaseResponse(data={}, headers=response.headers)
        return await self._handle_response(response)


async def get_supabase_client(
    request: Request, settings: Settings = Depends(get_settings)
) -> SupabaseClient:
    client: SupabaseClient | None = getattr(request.app.state, "supabase_client", None)
    if client is None:
        raise AppError("Supabase client not initialised", code="server_error", status_code=500)
    return client


__all__ = ["SupabaseClient", "SupabaseResponse", "get_supabase_client"]
