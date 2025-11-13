import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.config import Settings
from app.main import create_app


@pytest.mark.asyncio
async def test_preflight_allowed_when_origins_unset():
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_anon_key="anon",
        allowed_origins=[],
    )
    app = create_app(settings=settings)

    headers = {
        "origin": "http://example.com",
        "access-control-request-method": "POST",
        "access-control-request-headers": "content-type",
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options("/auth/signin", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["access-control-allow-origin"] == headers["origin"]


@pytest.mark.asyncio
async def test_preflight_allows_any_port_for_localhost_origin():
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_anon_key="anon",
        allowed_origins=["http://localhost"],
    )
    app = create_app(settings=settings)

    headers = {
        "origin": "http://localhost:5173",
        "access-control-request-method": "POST",
        "access-control-request-headers": "content-type",
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options("/auth/signin", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["access-control-allow-origin"] == headers["origin"]


@pytest.mark.asyncio
async def test_preflight_allows_any_port_for_loopback_origin_with_port():
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_anon_key="anon",
        allowed_origins=["http://127.0.0.1:3000"],
    )
    app = create_app(settings=settings)

    headers = {
        "origin": "http://127.0.0.1:5173",
        "access-control-request-method": "POST",
        "access-control-request-headers": "content-type",
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options("/auth/signin", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["access-control-allow-origin"] == headers["origin"]
