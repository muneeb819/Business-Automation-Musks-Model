import pytest


class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_register_user(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "TestPassword123!",
            "full_name": "New User",
        })
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, auth_client, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, auth_client, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!",
        })
        assert resp.status_code == 200
        assert resp.json()["access_token"]

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, auth_client, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me(self, auth_client):
        resp = await auth_client.get("/api/v1/auth/me")
        assert resp.status_code == 200, resp.text
        assert resp.json()["email"] == "test@example.com"
