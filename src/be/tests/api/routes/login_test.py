from unittest.mock import patch

import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.crud import create_user
from app.models import User, UserCreate
from app.utils import generate_password_reset_token
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture(scope="function")
async def login_db_session() -> AsyncSession:
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


@pytest.mark.asyncio
async def test_get_access_token(login_client) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await login_client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


@pytest.mark.asyncio
async def test_get_access_token_incorrect_password(login_client) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = await login_client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
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
async def test_recovery_password(login_client, login_normal_user_token_headers) -> None:
    with (
        patch("app.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.services.auth_service.send_email", return_value=None),
    ):
        email = "test@example.com"
        r = await login_client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=login_normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


@pytest.mark.asyncio
async def test_recovery_password_user_not_exits(
    login_client, login_normal_user_token_headers
) -> None:
    email = "jVgQr@example.com"
    r = await login_client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=login_normal_user_token_headers,
    )
    assert r.status_code == 200
    assert r.json() == {"message": "Password recovery email sent"}


@pytest.mark.asyncio
async def test_reset_password(login_client, login_db_session) -> None:
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
    await create_user(session=login_db_session, user_create=user_create)
    token = generate_password_reset_token(email=email)
    headers = await user_authentication_headers(client=login_client, email=email, password=password)
    data = {"new_password": new_password, "token": token}

    r = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

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
async def test_reset_password_invalid_token(login_client, login_superuser_token_headers) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = await login_client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=login_superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"
