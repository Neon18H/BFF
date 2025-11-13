import pytest
from httpx import Headers

from app.db.supabase_client import SupabaseResponse


@pytest.mark.asyncio
async def test_list_tasks(app):
    client, fake = app
    fake.rest_mapping[("GET", "tasks")] = SupabaseResponse(
        data=[
            {
                "id": "t1",
                "title": "Tarea",
                "description": "",
                "status": "sin_iniciar",
                "labels": [],
                "due_date": None,
                "add_to_calendar": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "order": 1000.0,
            }
        ],
        headers=Headers({"content-range": "0-0/1"}),
    )
    await client.post("/auth/signin", json={"email": "user@example.com", "password": "secret"})
    response = await client.get("/tasks")
    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == "t1"


@pytest.mark.asyncio
async def test_complete_task(app):
    client, fake = app
    fake.rest_mapping[("PATCH", "tasks?id=eq.t1")] = SupabaseResponse(
        data=[
            {
                "id": "t1",
                "title": "Tarea",
                "description": "",
                "status": "finalizado",
                "labels": [],
                "due_date": None,
                "add_to_calendar": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "order": 1000.0,
            }
        ],
        headers=Headers({}),
    )
    await client.post("/auth/signin", json={"email": "user@example.com", "password": "secret"})
    response = await client.post("/tasks/t1/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "finalizado"
