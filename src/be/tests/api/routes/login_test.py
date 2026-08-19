from unittest.mock import patch

import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.crud import create_user
from app.models import PasswordResetToken, RefreshToken, User, UserCreate
from app.repositories.user_repo import UserRepository
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture(scope="function")
async def login_db_session() -> AsyncSession:
    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_ASYNC_DATABASE_URI), echo=False, future=True
    )

    # Create all tables (including RefreshToken) — use sync conn for DDL
    from sqlmodel import SQLModel

    async with async_engine.connect() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.commit()

    async_session_maker = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    session = async_session_maker()

    try:
        try:
            user_statement = delete(UserCreate)
            await session.execute(user_statement)
            await session.commit()
        except Exception:
            await session.rollback()

        # Reset rate limiter to avoid 429s across test files
        from app.core.rate_limiter import reset_rate_limit

        reset_rate_limit()

        yield session
    finally:
        await session.close()
        await async_engine.dispose()


@pytest.fixture(scope="function")
async def login_client() -> httpx.AsyncClient:
    from app.main import app

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(scope="function")
async def login_superuser_token_headers(login_client, login_db_session) -> dict[str, str]:
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = await login_db_session.execute(statement)
    user = user_result.scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_active=True,
            is_superuser=True,
        )
        user = create_user(session=login_db_session, user_create=user_in)

    response = await login_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def login_normal_user_token_headers(login_client, login_db_session) -> dict[str, str]:
    email = random_email()
    password = random_lower_string()

    statement = select(User).where(User.email == email)
    user_result = await login_db_session.execute(statement)
    user = user_result.scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=email,
            full_name="Test User",
            password=password,
            is_active=True,
            is_superuser=False,
        )
        user = await create_user(session=login_db_session, user_create=user_in)

    response = await login_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": email,
            "password": password,
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def login_tokens(login_client) -> dict[str, str]:
    """Get both access and refresh tokens."""
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
    )
    return r.json()


@pytest.mark.asyncio
async def test_get_access_token(login_client) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


@pytest.mark.asyncio
async def test_login_returns_refresh_token(login_client) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "refresh_token" in tokens
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token_expires"] > 0
    assert tokens["refresh_token_expires"] > 0


@pytest.mark.asyncio
async def test_pkce_challenge(login_client) -> None:
    """Test that the PKCE challenge endpoint returns valid verifier/challenge."""
    r = await login_client.post(f"{settings.API_V1_STR}/login/pkce-challenge")
    assert r.status_code == 200
    data = r.json()
    assert "code_verifier" in data
    assert "code_challenge" in data
    assert data["code_challenge_method"] == "S256"

    # Verify S256: challenge = base64url(sha256(verifier))
    import base64
    import hashlib

    verifier = data["code_verifier"]
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    assert data["code_challenge"] == expected


@pytest.mark.asyncio
async def test_get_access_token_incorrect_password(login_client) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_use_access_token(login_client, login_superuser_token_headers) -> None:
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=login_superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


@pytest.mark.asyncio
async def test_refresh_token(login_client, login_tokens) -> None:
    """Test that a refresh token can be used to get a new access token."""
    refresh = login_tokens["refresh_token"]
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/refresh-token",
        json={"refresh_token": refresh},
    )
    assert r.status_code == 200
    result = r.json()
    assert "access_token" in result
    assert result["token_type"] == "bearer"
    assert result["access_token_expires"] > 0


@pytest.mark.asyncio
async def test_refresh_token_revoked(login_client, login_db_session, login_tokens) -> None:
    """Test that a revoked refresh token is rejected."""
    refresh = login_tokens["refresh_token"]

    # Revoke the refresh token
    result = await login_db_session.execute(
        select(RefreshToken).where(RefreshToken.token == refresh)
    )
    stored = result.scalar_one_or_none()
    if stored:
        stored.revoked = True
        await login_db_session.commit()

    r = await login_client.post(
        f"{settings.API_V1_STR}/login/refresh-token",
        json={"refresh_token": refresh},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_revoke_token(login_client, login_tokens, login_superuser_token_headers) -> None:
    """Test that a token can be revoked."""
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/revoke-token",
        headers=login_superuser_token_headers,
        json={"token": login_tokens["refresh_token"]},
    )
    assert r.status_code == 200
    assert r.json()["message"] == "Refresh token revoked"


@pytest.mark.asyncio
async def test_recovery_password(login_client, login_db_session) -> None:
    with (
        patch("app.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.services.auth_service.send_email", return_value=None),
    ):
        email = "test@example.com"
        r = await login_client.post(
            f"{settings.API_V1_STR}/password-recovery",
            json={"email": email},
        )
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


@pytest.mark.asyncio
async def test_recovery_password_user_not_exits(login_client, login_db_session) -> None:
    email = "jVgQr@example.com"
    r = await login_client.post(
        f"{settings.API_V1_STR}/password-recovery",
        json={"email": email},
    )
    assert r.status_code == 200
    assert r.json() == {"message": "Password recovery email sent"}


@pytest.mark.asyncio
async def test_reset_password(login_client, login_db_session) -> None:
    from app.repositories.user_repo import UserRepository

    email = random_email()
    password = "TestPass123!"
    new_password = "NewSecure456!"

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    await create_user(session=login_db_session, user_create=user_create)

    # Find the user to get their ID
    repo = UserRepository(session=login_db_session)
    user = await repo.get_by_email(email=email)

    # Generate a server-side token (not JWT-based like before)
    from datetime import datetime, timedelta, timezone
    import secrets

    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    db_token = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
    )

    login_db_session.add(db_token)
    await login_db_session.commit()

    data = {"new_password": new_password, "token": reset_token}

    r = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    # Verify the new password works for login
    auth_headers = await user_authentication_headers(
        client=login_client, email=email, password=new_password
    )
    r2 = await login_client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=auth_headers,
    )
    assert r2.status_code == 200
    result = r2.json()
    assert "email" in result


@pytest.mark.asyncio
async def test_reset_password_invalid_token(login_client) -> None:
    # Use a valid-complexity password so we get token validation error, not complexity error
    data = {"new_password": "ValidPass123!", "token": "invalid"}
    r = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        json=data,
    )

    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert "Invalid or expired reset token" in response["detail"]


@pytest.mark.asyncio
async def test_reset_password_token_single_use(login_client, login_db_session) -> None:
    """Test that a reset token can only be used once."""

    email = random_email()
    password = random_lower_string()
    new_password = "NewPass123!"
    another_new_password = "AnotherPass456!"

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    await create_user(session=login_db_session, user_create=user_create)

    # Find the user to get their ID
    repo = UserRepository(login_db_session)
    user = await repo.get_by_email(email=email)

    # Generate a server-side token
    import secrets
    from datetime import datetime, timedelta, timezone

    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    db_token = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
    )

    login_db_session.add(db_token)
    await login_db_session.commit()

    # First use should succeed
    data1 = {"new_password": new_password, "token": reset_token}
    r1 = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        json=data1,
    )
    assert r1.status_code == 200

    # Second use should fail (token already invalidated)
    data2 = {"new_password": another_new_password, "token": reset_token}
    r2 = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        json=data2,
    )
    assert r2.status_code == 400
    assert "Invalid or expired reset token" in r2.json()["detail"]


@pytest.mark.asyncio
async def test_reset_password_invalidates_all_user_tokens(login_client, login_db_session) -> None:
    """Test that a successful password reset invalidates all other tokens for the user."""

    email = random_email()
    password = random_lower_string()
    new_password = "NewPass123!"

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    await create_user(session=login_db_session, user_create=user_create)

    import secrets
    from datetime import datetime, timedelta, timezone

    # Find the user to get their ID
    repo = UserRepository(login_db_session)
    user = await repo.get_by_email(email=email)

    # Create two tokens for the same user
    token1 = secrets.token_urlsafe(32)
    token2 = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    db_token1 = PasswordResetToken(user_id=user.id, token=token1, expires_at=expires_at)
    db_token2 = PasswordResetToken(user_id=user.id, token=token2, expires_at=expires_at)

    login_db_session.add(db_token1)
    login_db_session.add(db_token2)
    await login_db_session.commit()

    # Use first token - should succeed and invalidate the second
    data1 = {"new_password": new_password, "token": token1}
    r1 = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        json=data1,
    )
    assert r1.status_code == 200

    # Second token should now be invalid
    data2 = {"new_password": "AnotherPass456!", "token": token2}
    r2 = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        json=data2,
    )
    assert r2.status_code == 400


@pytest.mark.asyncio
async def test_recovery_password_no_auth_required(login_client) -> None:
    """Test that password recovery endpoint doesn't require authentication."""
    with (
        patch("app.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.services.auth_service.send_email", return_value=None),
    ):
        # No auth headers - should still work
        r = await login_client.post(
            f"{settings.API_V1_STR}/password-recovery",
            json={"email": "test@example.com"},
        )
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_recovery_password_body_not_path(login_client) -> None:
    """Test that the recovery endpoint uses POST body, not URL path."""
    with (
        patch("app.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.services.auth_service.send_email", return_value=None),
    ):
        # Old style (URL path) should no longer work as expected
        r = await login_client.post(
            f"{settings.API_V1_STR}/password-recovery/test@example.com",
        )
        # Should get a 405 Method Not Allowed or similar, not a successful recovery
        assert r.status_code != 200 or "Password recovery" not in str(r.json())


@pytest.mark.asyncio
async def test_token_scopes(login_client, login_tokens) -> None:
    """Test that /login/token-scopes returns the scopes embedded in a JWT token."""
    access_token = login_tokens["access_token"]
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/token-scopes",
        json={"token": access_token},
    )
    assert r.status_code == 200
    data = r.json()
    assert "email" in data
    assert "scopes" in data
    assert isinstance(data["scopes"], list)
    assert len(data["scopes"]) > 0
    # Superuser should have all scopes
    assert "superuser" in data["scopes"]


@pytest.mark.asyncio
async def test_token_scopes_invalid_token(login_client) -> None:
    """Test that /login/token-scopes rejects invalid tokens."""
    r = await login_client.post(
        f"{settings.API_V1_STR}/login/token-scopes",
        json={"token": "invalid.token.here"},
    )
    assert r.status_code == 401
