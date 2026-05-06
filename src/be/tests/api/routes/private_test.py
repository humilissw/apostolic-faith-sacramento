from typing import AsyncGenerator

import httpx
import pytest
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.core.db import get_db_session
from app.main import app
from app.models import User


@pytest.fixture(scope="function")
async def private_client(db_session: AsyncSession) -> httpx.AsyncClient:
    """Test client that shares the test's db_session with the app."""

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_user(
    db_session: AsyncSession,
) -> None:
    import uuid

    from app.crud import create_user
    from app.models import UserCreate

    test_email = f"pollo_{uuid.uuid4().hex[:8]}@listo.com"

    # Ensure superuser exists in the test db so the login endpoint can find it
    stmt = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = await db_session.execute(stmt)
    superuser = user_result.scalar_one_or_none()
    if not superuser:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_active=True,
            is_superuser=True,
        )
        superuser = await create_user(session=db_session, user_create=user_in)
        await db_session.commit()
        await db_session.refresh(superuser)

    # Make login + create-user requests using the same overridden db_session
    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        response = await c.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={
                "username": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            },
        )
        token = response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        r = await c.post(
            f"{settings.API_V1_STR}/private/users/",
            headers=auth_headers,
            json={
                "email": test_email,
                "password": "password123",
                "full_name": "Pollo Listo",
            },
        )

    app.dependency_overrides.clear()

    assert r.status_code == 200

    result = await db_session.execute(select(User).where(User.email == test_email))
    user = result.scalar_one_or_none()

    assert user
    assert user.email == test_email
    assert user.full_name == "Pollo Listo"
