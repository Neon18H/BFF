import pytest
from httpx import Headers

from app.db.supabase_client import SupabaseResponse


@pytest.mark.asyncio
async def test_list_clients(app, headers):
    client, fake = app
    fake.rest_mapping[("GET", "clients")] = SupabaseResponse(
        data=[
            {
                "id": "c1",
                "name_or_business": "Cliente 1",
                "identificacion": "123",
                "contact": None,
                "notes": None,
                "payment_state": "pendiente",
                "payment_amount": None,
                "tags": [],
                "documents": [],
                "tax_profile": None,
            }
        ],
        headers=headers,
    )
    await client.post("/auth/signin", json={"email": "user@example.com", "password": "secret"})
    response = await client.get("/clients")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["items"][0]["nameOrBusiness"] == "Cliente 1"


@pytest.mark.asyncio
async def test_create_client(app):
    client, fake = app
    fake.rest_mapping[("POST", "clients")] = SupabaseResponse(
        data=[
            {
                "id": "c1",
                "name_or_business": "Cliente 1",
                "identificacion": "123",
                "contact": None,
                "notes": None,
                "payment_state": "pendiente",
                "payment_amount": None,
                "tags": [],
                "documents": [],
                "tax_profile": None,
            }
        ],
        headers=Headers({}),
    )
    await client.post("/auth/signin", json={"email": "user@example.com", "password": "secret"})
    response = await client.post(
        "/clients",
        json={
            "nameOrBusiness": "Cliente 1",
            "identificacion": "123",
            "paymentState": "pendiente",
        },
    )
    assert response.status_code == 201
    assert response.json()["id"] == "c1"
