import pytest
import pytest_asyncio
from httpx import AsyncClient, Headers

from app.core.config import Settings
from app.db.supabase_client import SupabaseResponse, get_supabase_client
from app.main import create_app


class FakeSupabaseClient:
    def __init__(self):
        self.sign_in_payload = {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {"id": "user-1", "email": "user@example.com"},
        }
        self.refresh_payload = self.sign_in_payload
        self.user_payload = {"id": "user-1", "email": "user@example.com"}
        self.rest_mapping = {}

    async def auth_sign_in(self, email: str, password: str):
        return self.sign_in_payload

    async def auth_refresh(self, refresh_token: str):
        return self.refresh_payload

    async def auth_get_user(self, access_token: str):
        return {"user": self.user_payload}

    async def auth_sign_out(self, access_token: str):
        return None

    async def rest_request(self, method, path, access_token, params=None, json=None, headers=None):
        key = (method, path)
        response = self.rest_mapping.get(key)
        if response is None:
            return SupabaseResponse(data=[], headers=Headers({"content-range": "0-0/0"}))
        return response


@pytest_asyncio.fixture
async def app(monkeypatch):
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_anon_key="anon",
        allowed_origins=["http://localhost"],
    )
    application = create_app(settings=settings)
    fake_client = FakeSupabaseClient()

    async def _override():
        return fake_client

    application.dependency_overrides[get_supabase_client] = _override

    async with AsyncClient(app=application, base_url="http://test") as client:
        yield client, fake_client


@pytest.fixture
def headers():
    return Headers({"content-range": "0-1/2"})
