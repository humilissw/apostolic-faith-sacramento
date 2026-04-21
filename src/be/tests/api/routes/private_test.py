import httpx
import pytest
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.main import app
from app.models import User


@pytest.fixture(scope="function")
async def private_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_create_user(private_client: httpx.AsyncClient, superuser_token_headers, db_session: AsyncSession) -> None:
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

    data = r.json()

    result = await db_session.execute(select(User).where(User.email == test_email))
    user = result.scalar_one_or_none()

    assert user
    assert user.email == test_email
    assert user.full_name == "Pollo Listo"
