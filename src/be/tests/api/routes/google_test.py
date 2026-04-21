import pytest
from httpx import ASGITransport
from fastapi.responses import RedirectResponse
from unittest.mock import AsyncMock, patch

from app.main import app
import httpx


@pytest.fixture(scope="function")
async def google_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_google_login_route(google_client) -> None:
    with patch("app.api.routes.google.oauth") as mock_oauth:
        mock_oauth.google.authorize_redirect = AsyncMock(
            return_value=RedirectResponse(url="https://google.com/oauth")
        )

        response = await google_client.get("/api/v1/google/login/google")
        assert response.status_code == 307


@pytest.mark.asyncio
async def test_google_auth_route(google_client) -> None:
    with patch("app.api.routes.google.oauth") as mock_oauth:
        mock_token = {"userinfo": {"email": "test@example.com", "name": "Test User"}}
        mock_oauth.google.authorize_access_token = AsyncMock(return_value=mock_token)

        response = await google_client.get("/api/v1/google/auth/google")
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
        assert response.json()["name"] == "Test User"
