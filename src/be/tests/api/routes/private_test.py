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
    private_client: httpx.AsyncClient, superuser_token_headers, db_session: AsyncSession
) -> None:
    import uuid

    test_email = f"pollo_{uuid.uuid4().hex[:8]}@listo.com"
    r = await private_client.post(
        f"{settings.API_V1_STR}/private/users/",
        headers=superuser_token_headers,
        json={
            "email": test_email,
            "password": "password123",
            "full_name": "Pollo Listo",
        },
    )

    assert r.status_code == 200

    result = await db_session.execute(select(User).where(User.email == test_email))
    user = result.scalar_one_or_none()

    assert user
    assert user.email == test_email
    assert user.full_name == "Pollo Listo"
