from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, delete

from app.config import settings
from app.core.db import async_engine, init_db_async
from app.main import app
from app.models import Item, User
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="session", autouse=True)
async def async_db() -> Generator[AsyncSession, None, None]:
    """Async database session fixture for async operations."""
    async with AsyncSession(async_engine) as session:
        await init_db_async(async_engine)
        yield session
        # Clean up after tests
        statement = delete(Item)
        await session.execute(statement)
        statement = delete(User)
        await session.execute(statement)
        await session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="function")
async def db_session(async_db: AsyncSession) -> AsyncSession:
    """Function-scoped async database session for individual tests."""
    yield async_db
    # Clean up after each test
    await async_db.rollback()
