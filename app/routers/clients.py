from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.security import AuthContext, get_auth_context
from app.db.supabase_client import SupabaseClient, get_supabase_client
from app.models.clients import Client, ClientCreate, ClientList, ClientUpdate
from app.services.clients_service import ClientsService

router = APIRouter(prefix="/clients", tags=["clients"])


def get_clients_service(supabase: SupabaseClient = Depends(get_supabase_client)) -> ClientsService:
    return ClientsService(supabase)


@router.get("", response_model=ClientList)
async def list_clients(
    auth: AuthContext = Depends(get_auth_context),
    service: ClientsService = Depends(get_clients_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(default=None),
) -> ClientList:
    return await service.list_clients(
        auth.access_token,
        page=page,
        page_size=page_size,
        q=q,
    )


@router.get("/{client_id}", response_model=Client)
async def get_client(
    client_id: str,
    auth: AuthContext = Depends(get_auth_context),
    service: ClientsService = Depends(get_clients_service),
) -> Client:
    return await service.get_client(auth.access_token, client_id)


@router.post("", response_model=Client, status_code=201)
async def create_client(
    payload: ClientCreate,
    auth: AuthContext = Depends(get_auth_context),
    service: ClientsService = Depends(get_clients_service),
) -> Client:
    return await service.create_client(auth.access_token, payload)


@router.put("/{client_id}", response_model=Client)
async def update_client(
    client_id: str,
    payload: ClientUpdate,
    auth: AuthContext = Depends(get_auth_context),
    service: ClientsService = Depends(get_clients_service),
) -> Client:
    return await service.update_client(auth.access_token, client_id, payload)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_client(
    client_id: str,
    auth: AuthContext = Depends(get_auth_context),
    service: ClientsService = Depends(get_clients_service),
) -> Response:
    await service.delete_client(auth.access_token, client_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
