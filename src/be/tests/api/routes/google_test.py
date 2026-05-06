from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport

from app.main import app
import httpx
import sys

# Fake google module so tests can patch google.auth.jwt
_google_auth_jwt = MagicMock()


def _make_fake_verify_id_token(payload: dict):
    def fake_verify(id_token, client_id=None):
        return (MagicMock(), payload)

    return fake_verify


_google_auth_jwt.verify_id_token = _make_fake_verify_id_token(
    {"email": "test@example.com", "email_verified": True}
)
_google_auth_pkg = MagicMock()
_google_auth_pkg.jwt = _google_auth_jwt
_google_pkg = MagicMock()
_google_pkg.auth = _google_auth_pkg
sys.modules.setdefault("google", _google_pkg)
sys.modules.setdefault("google.auth", _google_auth_pkg)
sys.modules.setdefault("google.auth.jwt", _google_auth_jwt)


def _mock_db_session():
    """Dependency override for database session in google tests."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = None
    mock_session = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    return mock_session


@pytest.fixture(scope="function")
async def google_client():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        c.cookies.set("google_code_verifier", "fakewriter", path="/")
        from app.core.db import get_db_session

        app.dependency_overrides[get_db_session] = _mock_db_session
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def google_client_no_pkce():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        from app.core.db import get_db_session

        app.dependency_overrides[get_db_session] = _mock_db_session
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_google_login_requires_config(google_client) -> None:
    """Google login should return 501 when not configured."""
    with patch("app.config.settings.GOOGLE_CLIENT_ID", "dummy"):
        response = await google_client.get("/api/v1/google/login/google")
        assert response.status_code == 501


@pytest.mark.asyncio
async def test_google_login_returns_redirect_with_pkce_cookie(google_client) -> None:
    """Google login should redirect to Google with PKCE params and code_verifier cookie."""
    from starlette.responses import RedirectResponse

    real_redirect = RedirectResponse(url="https://accounts.google.com/oauth/auth")
    real_redirect.set_cookie = MagicMock()

    mock_oauth = MagicMock()
    mock_oauth.google = MagicMock()
    mock_oauth.google.authorize_redirect = AsyncMock(return_value=real_redirect)

    with (
        patch("app.config.settings.GOOGLE_CLIENT_ID", "test-client-id"),
        patch("app.config.settings.GOOGLE_CLIENT_SECRET", "test-secret"),
        patch("app.config.settings.DOMAIN", "http://localhost:8000"),
        patch("app.config.settings.API_V1_STR", "/api/v1"),
        patch("app.api.routes.google._build_oauth", return_value=mock_oauth),
    ):
        response = await google_client.get("/api/v1/google/login/google")
        assert response.status_code == 307

    call_kwargs = mock_oauth.google.authorize_redirect.call_args
    assert call_kwargs[1]["code_challenge_method"] == "S256"
    assert call_kwargs[1]["code_challenge"]
    assert len(call_kwargs[1]["code_challenge"]) > 0

    real_redirect.set_cookie.assert_called_once()
    cookie_call = real_redirect.set_cookie.call_args
    assert cookie_call[1]["httponly"] is True
    assert cookie_call[1]["secure"] is True
    assert cookie_call[1]["samesite"] == "lax"


@pytest.mark.asyncio
async def test_google_auth_returns_redirect_with_tokens(google_client) -> None:
    """Google OAuth callback should redirect to frontend with httpOnly cookies."""
    mock_payload = {"email": "test@example.com", "name": "Test User", "email_verified": True}
    mock_credentials = MagicMock()
    mock_new_user = MagicMock()
    mock_new_user.id = 2
    mock_new_user.email = "test@example.com"
    mock_new_user.is_active = True

    with (
        patch("app.config.settings.GOOGLE_CLIENT_ID", "test-client-id"),
        patch("app.config.settings.GOOGLE_CLIENT_SECRET", "test-secret"),
        patch("app.config.settings.DOMAIN", "http://localhost:8000"),
        patch("app.config.settings.API_V1_STR", "/api/v1"),
        patch("app.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES", 30),
        patch("app.config.settings.REFRESH_TOKEN_EXPIRE_DAYS", 30),
        patch("app.config.settings.JWT_ISSUER", "test-issuer"),
        patch("app.config.settings.JWT_AUDIENCE", "test-audience"),
        patch("app.config.settings.FRONTEND_HOST", "http://localhost:3000"),
        patch("google.auth.jwt.verify_id_token", return_value=(mock_credentials, mock_payload)),
        patch("app.api.routes.google.UserRepository") as mock_repo_cls,
        patch("app.crud.create_user", return_value=mock_new_user),
    ):
        mock_repo_cls.return_value.get_by_email = AsyncMock(return_value=None)

        with patch(
            "authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token",
            new_callable=AsyncMock,
            return_value={"id_token": "fake.id.token"},
        ):
            response = await google_client.get(
                "/api/v1/google/auth/google?code=mock_code&state=mock_state"
            )
            assert response.status_code == 302
            location = response.headers.get("location", "")
            assert "http://localhost:3000/google-callback" in location
            # Tokens are now set as httpOnly cookies, not in URL
            set_cookie = response.headers.get("set-cookie", "")
            assert "access_token=" in set_cookie
            assert "refresh_token=" in set_cookie
            assert "httponly" in set_cookie.lower()


@pytest.mark.asyncio
async def test_google_auth_rejects_unverified_email(google_client) -> None:
    """Google OAuth should reject users with unverified emails."""
    mock_unverified = {"email": "test@example.com", "email_verified": False}
    mock_creds = MagicMock()

    with (
        patch("app.config.settings.GOOGLE_CLIENT_ID", "test-client-id"),
        patch("app.config.settings.GOOGLE_CLIENT_SECRET", "test-secret"),
        patch("google.auth.jwt.verify_id_token", return_value=(mock_creds, mock_unverified)),
        patch("app.api.routes.google.UserRepository") as mock_repo_cls,
    ):
        mock_repo_cls.return_value.get_by_email = AsyncMock(return_value=None)

        with patch(
            "authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token",
            new_callable=AsyncMock,
            return_value={"id_token": "fake.id.token"},
        ):
            response = await google_client.get(
                "/api/v1/google/auth/google?code=mock_code&state=mock_state"
            )
            assert response.status_code == 400
            assert "verified" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_google_auth_rejects_missing_id_token(google_client) -> None:
    """Google OAuth should reject responses without an ID token."""

    with (
        patch("app.config.settings.GOOGLE_CLIENT_ID", "test-client-id"),
        patch("app.config.settings.GOOGLE_CLIENT_SECRET", "test-secret"),
        patch("app.api.routes.google.UserRepository") as mock_repo_cls,
    ):
        mock_repo_cls.return_value.get_by_email = AsyncMock(return_value=None)

        with patch(
            "authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token",
            new_callable=AsyncMock,
            return_value={},  # No id_token
        ):
            response = await google_client.get(
                "/api/v1/google/auth/google?code=mock_code&state=mock_state"
            )
            assert response.status_code == 400
            assert "ID token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_google_auth_rejects_missing_pkce_cookie(google_client_no_pkce) -> None:
    """Google OAuth callback should reject missing code_verifier cookie."""

    with patch("app.config.settings.GOOGLE_CLIENT_ID", "test-client-id"):
        with patch(
            "authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token",
            new_callable=AsyncMock,
            return_value={"id_token": "fake.id.token"},
        ):
            with patch("app.api.routes.google.UserRepository") as mock_repo_cls:
                mock_repo_cls.return_value.get_by_email = AsyncMock(return_value=None)
                response = await google_client_no_pkce.get(
                    "/api/v1/google/auth/google?code=mock_code&state=mock_state"
                )
                assert response.status_code == 400
                assert "PKCE" in response.json()["detail"]


@pytest.mark.asyncio
async def test_google_auth_auto_provisions_user(google_client) -> None:
    """Google OAuth should auto-create users who don't exist in the database."""
    mock_payload = {
        "email": "newuser@example.com",
        "name": "New User",
        "email_verified": True,
    }
    mock_creds = MagicMock()
    mock_existing_user = MagicMock()
    mock_existing_user.id = 42
    mock_existing_user.email = "newuser@example.com"
    mock_existing_user.is_active = True

    with (
        patch("app.config.settings.GOOGLE_CLIENT_ID", "test-client-id"),
        patch("app.config.settings.GOOGLE_CLIENT_SECRET", "test-secret"),
        patch("app.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES", 30),
        patch("app.config.settings.REFRESH_TOKEN_EXPIRE_DAYS", 30),
        patch("app.config.settings.JWT_ISSUER", "test-issuer"),
        patch("app.config.settings.JWT_AUDIENCE", "test-audience"),
        patch("app.config.settings.FRONTEND_HOST", "http://localhost:3000"),
        patch("google.auth.jwt.verify_id_token", return_value=(mock_creds, mock_payload)),
        patch("app.api.routes.google.UserRepository") as mock_repo_cls,
    ):
        mock_repo_cls.return_value.get_by_email = AsyncMock(return_value=mock_existing_user)

        with patch(
            "authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token",
            new_callable=AsyncMock,
            return_value={"id_token": "fake.id.token"},
        ):
            response = await google_client.get(
                "/api/v1/google/auth/google?code=mock_code&state=mock_state"
            )
            assert response.status_code == 302
            # Token is now set as httpOnly cookie, not in URL
            set_cookie = response.headers.get("set-cookie", "")
            assert "access_token=" in set_cookie
