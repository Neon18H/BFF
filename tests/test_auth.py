import pytest


@pytest.mark.asyncio
async def test_signin_sets_cookies(app):
    client, _ = app
    response = await client.post(
        "/auth/signin",
        json={"email": "user@example.com", "password": "secret"},
    )
    assert response.status_code == 200
    assert "sb-access-token" in response.cookies
    assert response.json()["access_token"] == "access"


@pytest.mark.asyncio
async def test_me_requires_cookie(app):
    client, _ = app
    await client.post("/auth/signin", json={"email": "user@example.com", "password": "secret"})
    response = await client.get("/auth/me")
    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["email"] == "user@example.com"
