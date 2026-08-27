"""Tests for admin password reset endpoint."""

from unittest.mock import patch

import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.crud import create_user
from app.models import User, UserCreate
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture(scope="function")
async def admin_reset_db_session() -> AsyncSession:
    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_ASYNC_DATABASE_URI), echo=False, future=True
    )

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

        # Clear feature flags table so disabled tests start clean
        try:
            from app.models import FeatureFlag

            flag_statement = delete(FeatureFlag)
            await session.execute(flag_statement)
            await session.commit()
        except Exception:
            await session.rollback()

        from app.core.rate_limiter import reset_rate_limit

        reset_rate_limit()

        yield session
    finally:
        await session.close()
        await async_engine.dispose()


@pytest.fixture(scope="function")
async def admin_reset_client() -> httpx.AsyncClient:
    from app.main import app

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(scope="function")
async def admin_reset_superuser_token_headers(
    admin_reset_client, admin_reset_db_session
) -> dict[str, str]:
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = await admin_reset_db_session.execute(statement)
    user = user_result.scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_active=True,
            is_superuser=True,
        )
        user = await create_user(session=admin_reset_db_session, user_create=user_in)
    else:
        # Keep the stored hash in sync with .env (fresh DBs / rotated passwords)
        from app.core.security import get_password_hash, verify_password

        if not verify_password(settings.FIRST_SUPERUSER_PASSWORD, user.hashed_password):
            user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            user.is_superuser = True
            admin_reset_db_session.add(user)
            await admin_reset_db_session.commit()

    response = await admin_reset_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def admin_reset_normal_user_token_headers(
    admin_reset_client, admin_reset_db_session
) -> dict[str, str]:
    email = random_email()
    password = random_lower_string()

    statement = select(User).where(User.email == email)
    user_result = await admin_reset_db_session.execute(statement)
    user = user_result.scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=email,
            full_name="Test User",
            password=password,
            is_active=True,
            is_superuser=False,
        )
        user = await create_user(session=admin_reset_db_session, user_create=user_in)

    response = await admin_reset_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": email,
            "password": password,
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.mark.asyncio
async def test_admin_password_reset_enabled_succeeds(
    admin_reset_client, admin_reset_db_session, admin_reset_superuser_token_headers
) -> None:
    """Test that admin password reset works when feature flag is enabled."""
    # Pre-seed the feature flags to enable them (including our new one)
    pre_seed_response = await admin_reset_client.post(
        f"{settings.API_V1_STR}/feature-flags/pre-seed",
        headers=admin_reset_superuser_token_headers,
    )
    assert pre_seed_response.status_code == 200

    with (
        patch("app.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.services.auth_service.send_email", return_value=None),
    ):
        email = random_email()
        # Create the target user
        user_create = UserCreate(
            email=email,
            full_name="Test User",
            password="TempPass123!",
            is_active=True,
            is_superuser=False,
        )
        await create_user(session=admin_reset_db_session, user_create=user_create)

        r = await admin_reset_client.post(
            f"{settings.API_V1_STR}/admin/password-reset",
            json={"email": email},
            headers=admin_reset_superuser_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


@pytest.mark.asyncio
async def test_admin_password_reset_disabled_returns_403(
    admin_reset_client, admin_reset_db_session, admin_reset_superuser_token_headers
) -> None:
    """Test that admin password reset returns 403 when feature flag is disabled."""
    # Do NOT pre-seed feature flags — they should be disabled by default
    r = await admin_reset_client.post(
        f"{settings.API_V1_STR}/admin/password-reset",
        json={"email": "test@example.com"},
        headers=admin_reset_superuser_token_headers,
    )
    assert r.status_code == 403
    assert "disabled" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_password_reset_non_superuser_forbidden(
    admin_reset_client, admin_reset_db_session, admin_reset_normal_user_token_headers
) -> None:
    """Test that non-superusers cannot call the admin password reset endpoint."""
    with (
        patch("app.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.services.auth_service.send_email", return_value=None),
    ):
        email = random_email()
        user_create = UserCreate(
            email=email,
            full_name="Test User",
            password="TempPass123!",
            is_active=True,
            is_superuser=False,
        )
        await create_user(session=admin_reset_db_session, user_create=user_create)

        r = await admin_reset_client.post(
            f"{settings.API_V1_STR}/admin/password-reset",
            json={"email": email},
            headers=admin_reset_normal_user_token_headers,
        )
        # Should get 403 because the endpoint requires superuser
        assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_password_reset_invalid_email_format(
    admin_reset_client, admin_reset_db_session, admin_reset_superuser_token_headers
) -> None:
    """Test that invalid email format is rejected."""
    # Pre-seed feature flags first
    await admin_reset_client.post(
        f"{settings.API_V1_STR}/feature-flags/pre-seed",
        headers=admin_reset_superuser_token_headers,
    )

    r = await admin_reset_client.post(
        f"{settings.API_V1_STR}/admin/password-reset",
        json={"email": "not-an-email"},
        headers=admin_reset_superuser_token_headers,
    )
    assert r.status_code == 400
    assert "Invalid email format" in r.json()["detail"]


@pytest.mark.asyncio
async def test_admin_password_reset_nonexistent_user_no_error(
    admin_reset_client, admin_reset_db_session, admin_reset_superuser_token_headers
) -> None:
    """Test that requesting reset for a non-existent user doesn't reveal that fact."""
    # Pre-seed feature flags first
    await admin_reset_client.post(
        f"{settings.API_V1_STR}/feature-flags/pre-seed",
        headers=admin_reset_superuser_token_headers,
    )

    with (
        patch("app.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.services.auth_service.send_email", return_value=None),
    ):
        r = await admin_reset_client.post(
            f"{settings.API_V1_STR}/admin/password-reset",
            json={"email": "nonexistent@example.com"},
            headers=admin_reset_superuser_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


@pytest.mark.asyncio
async def test_admin_password_reset_no_auth_required(admin_reset_client) -> None:
    """Test that the admin password reset endpoint requires authentication."""
    r = await admin_reset_client.post(
        f"{settings.API_V1_STR}/admin/password-reset",
        json={"email": "test@example.com"},
    )
    assert r.status_code in (401, 403)
