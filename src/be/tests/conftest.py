from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.db import async_engine, init_db_async
from app.main import app
from app.models import Item, User, Media, VideoUpload
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session")
async def db() -> Generator[AsyncSession, None, None]:
    """Session-scoped database fixture for all tests."""
    # Initialize database using async engine
    await init_db_async(async_engine)

    # Create async session
    async_session_maker = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with async_session_maker() as session:
        yield session
        # Clean up after all tests
        try:
            statement = delete(Item)
            await session.execute(statement)
            statement = delete(User)
            await session.execute(statement)
            statement = delete(Media)
            await session.execute(statement)
            statement = delete(VideoUpload)
            await session.execute(statement)
            await session.commit()
        except Exception:
            await session.rollback()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Module-scoped test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Superuser authentication headers."""
    # Ensure superuser exists
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db_async(async_engine))
    loop.close()

    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: AsyncSession) -> dict[str, str]:
    """Normal user authentication headers."""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="function")
async def db_session(db: AsyncSession) -> AsyncSession:
    """Function-scoped database session for individual tests."""
    # Create a fresh session for each test
    async_session_maker = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    test_session = async_session_maker()

    try:
        yield test_session
    finally:
        # Clean up after each test
        try:
            statement = delete(Item)
            await test_session.execute(statement)
            statement = delete(User)
            await test_session.execute(statement)
            statement = delete(Media)
            await test_session.execute(statement)
            statement = delete(VideoUpload)
            await test_session.execute(statement)
            await test_session.commit()
        except Exception:
            await test_session.rollback()
        finally:
            await test_session.close()