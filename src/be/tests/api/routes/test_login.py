import asyncio
from typing import Annotated, AsyncGenerator
from unittest.mock import patch

import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.crud import create_user
from app.models import User, UserCreate
from app.utils import generate_password_reset_token
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test."""
    loop = pytest.plugins.asyncio._get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Function-scoped database session for individual tests."""
    # Create async engine in the test's event loop
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy import delete

    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_ASYNC_DATABASE_URI), echo=False, future=True
    )
    async_session_maker = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    session = async_session_maker()

    try:
        # Clean up User table
        try:
            user_statement = delete(UserCreate)
            await session.execute(user_statement)
            await session.commit()
        except Exception:
            await session.rollback()

        yield session
    finally:
        await session.close()
        await async_engine.dispose()


@pytest.fixture(scope="function")
async def client() -> httpx.AsyncClient:
    """Function-scoped async test client."""
    from app.main import app

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(scope="function")
async def superuser_token_headers(client: httpx.AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    """Superuser authentication headers."""
    from sqlalchemy import select

    # Ensure superuser exists
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = await db_session.execute(statement)
    user = user_result.scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_active=True,
            is_superuser=True,
        )
        user = create_user(session=db_session, user_create=user_in)

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def normal_user_token_headers(client: httpx.AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    """Normal user authentication headers."""
    from sqlalchemy import select

    # Ensure normal user exists
    email = random_email()
    password = random_lower_string()

    statement = select(User).where(User.email == email)
    user_result = await db_session.execute(statement)
    user = user_result.scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=email,
            full_name="Test User",
            password=password,
            is_active=True,
            is_superuser=False,
        )
        user = await create_user(session=db_session, user_create=user_in)

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": email,
            "password": password,
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def test_get_access_token(client: httpx.AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


async def test_get_access_token_incorrect_password(client: httpx.AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 400


async def test_use_access_token(
    client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


async def test_recovery_password(
    client: httpx.AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    with patch("app.config.settings.SMTP_HOST", "smtp.example.com"):
        email = "test@example.com"
        r = await client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


async def test_recovery_password_user_not_exits(
    client: httpx.AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    email = "jVgQr@example.com"
    r = await client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    # Security: don't reveal if user exists, return 200 OK
    assert r.status_code == 200
    assert r.json() == {"message": "Password recovery email sent"}


async def test_reset_password(client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    await create_user(session=db_session, user_create=user_create)
    token = generate_password_reset_token(email=email)
    headers = await user_authentication_headers(client=client, email=email, password=password)
    data = {"new_password": new_password, "token": token}

    r = await client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    # Re-authenticate with the new password to verify it works
    auth_headers = await user_authentication_headers(client=client, email=email, password=new_password)
    r2 = await client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=auth_headers,
    )
    assert r2.status_code == 200
    result = r2.json()
    assert "email" in result


async def test_reset_password_invalid_token(
    client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = await client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"
