from __future__ import annotations

from typing import Dict, Optional

from app.core.errors import AppError
from app.db.supabase_client import SupabaseClient
from app.models.clients import Client, ClientCreate, ClientList, ClientUpdate


class ClientsService:
    def __init__(self, supabase: SupabaseClient):
        self._supabase = supabase

    @staticmethod
    def _parse_total(headers) -> int:
        content_range = headers.get("content-range")
        if not content_range:
            return 0
        try:
            _, total = content_range.split("/")
            return int(total)
        except ValueError:
            return 0

    async def list_clients(
        self,
        access_token: str,
        *,
        page: int = 1,
        page_size: int = 20,
        q: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
    ) -> ClientList:
        start = (page - 1) * page_size
        end = start + page_size - 1
        params: Dict[str, str] = {"select": "*", "order": "name_or_business"}
        if q:
            params["or"] = f"(name_or_business.ilike.*{q}*,notes.ilike.*{q}*)"
        if filters:
            params.update(filters)
        headers = {"Range": f"{start}-{end}", "Prefer": "count=exact"}
        response = await self._supabase.rest_request(
            "GET", "clients", access_token, params=params, headers=headers
        )
        data = response.data
        if not isinstance(data, list):
            raise AppError("Invalid response from Supabase", code="supabase_error", status_code=502)
        total = self._parse_total(response.headers)
        return ClientList(
            items=[Client.model_validate(i) for i in data],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_client(self, access_token: str, client_id: str) -> Client:
        params = {"select": "*", "id": f"eq.{client_id}"}
        response = await self._supabase.rest_request(
            "GET", "clients", access_token, params=params, headers={"Range": "0-0"}
        )
        data = response.data
        if isinstance(data, list) and data:
            return Client.model_validate(data[0])
        raise AppError("Client not found", code="not_found", status_code=404)

    async def create_client(self, access_token: str, payload: ClientCreate) -> Client:
        response = await self._supabase.rest_request(
            "POST",
            "clients",
            access_token,
            json=[payload.model_dump(by_alias=False)],
            headers={"Prefer": "return=representation"},
        )
        data = response.data
        if isinstance(data, list) and data:
            return Client.model_validate(data[0])
        raise AppError("Unable to create client", code="supabase_error", status_code=502)

    async def update_client(
        self, access_token: str, client_id: str, payload: ClientUpdate
    ) -> Client:
        response = await self._supabase.rest_request(
            "PATCH",
            f"clients?id=eq.{client_id}",
            access_token,
            json=payload.model_dump(exclude_none=True, by_alias=False),
            headers={"Prefer": "return=representation"},
        )
        data = response.data
        if isinstance(data, list) and data:
            return Client.model_validate(data[0])
        raise AppError("Client not found", code="not_found", status_code=404)

    async def delete_client(self, access_token: str, client_id: str) -> None:
        await self._supabase.rest_request("DELETE", f"clients?id=eq.{client_id}", access_token)


__all__ = ["ClientsService"]
