"""Tests for feature flag endpoints, focusing on cookie-based auth.

Regression tests: the web app stores tokens only in httpOnly cookies and never
sends an Authorization header. Previously the OAuth2PasswordBearer dependency
raised 401 for such requests before the cookie fallback could run, so
GET /api/v1/feature-flags/ returned 401 with a valid cookie.
"""

import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.crud import create_user
from app.models import User, UserCreate, UserScope


@pytest.fixture(scope="function")
async def flags_db_session() -> AsyncSession:
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

        from app.core.rate_limiter import reset_rate_limit

        reset_rate_limit()

        yield session
    finally:
        await session.close()
        await async_engine.dispose()


@pytest.fixture(scope="function")
async def flags_client() -> httpx.AsyncClient:
    from app.main import app

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def _ensure_superuser(client, session) -> None:
    """Ensure the superuser exists with the 'superuser' scope row."""
    stmt = select(User).where(User.email == settings.FIRST_SUPERUSER)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_active=True,
            is_superuser=True,
        )
        user = await create_user(session=session, user_create=user_in)
    has_scope = await session.execute(
        select(UserScope).where(
            UserScope.user_id == user.id,  # type: ignore[arg-type]
            UserScope.scope == "superuser",  # type: ignore[arg-type]
        )
    )
    if not has_scope.scalar_one_or_none():
        session.add(UserScope(user_id=user.id, scope="superuser"))  # type: ignore[arg-type]
        await session.commit()


async def _login_via_password_grant(client) -> None:
    r = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_feature_flags_list_cookie_only(flags_client, flags_db_session) -> None:
    """GET /feature-flags/ must succeed with a valid cookie and NO Authorization header.

    This is the exact reported bug: 401 on the feature flag endpoint despite a
    valid access token in the httpOnly cookie.
    """
    await _ensure_superuser(flags_client, flags_db_session)
    await _login_via_password_grant(flags_client)

    # No Authorization header — the httpx client jar carries the Set-Cookie values
    r = await flags_client.get(f"{settings.API_V1_STR}/feature-flags/")
    assert (
        r.status_code == 200
    ), f"expected 200 with cookie-only auth, got {r.status_code}: {r.text}"
    body = r.json()
    assert "data" in body and "count" in body


@pytest.mark.asyncio
async def test_feature_flags_list_without_any_token_returns_401(
    flags_client, flags_db_session
) -> None:
    """No token in header or cookie → 401 'Not authenticated'."""
    r = await flags_client.get(f"{settings.API_V1_STR}/feature-flags/")
    assert r.status_code == 401
    assert r.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_feature_flags_list_non_superuser_cookie_only_returns_403(
    flags_client, flags_db_session
) -> None:
    """A non-superuser with a valid cookie must get 403 (not 401)."""
    email = "non-super-flag-test@example.com"
    password = "test-password-123"

    stmt = select(User).where(User.email == email)
    result = await flags_db_session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user_in = UserCreate(
            email=email,
            password=password,
            is_active=True,
            is_superuser=False,
        )
        user = await create_user(session=flags_db_session, user_create=user_in)

    r = await flags_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200

    # Cookie-only auth as a non-superuser → superuser scope check must reject with 403
    r = await flags_client.get(f"{settings.API_V1_STR}/feature-flags/")
    assert r.status_code == 403, f"expected 403 for non-superuser, got {r.status_code}: {r.text}"
