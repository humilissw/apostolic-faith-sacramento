import pytest
from httpx import ASGITransport
import httpx

from app.config import settings
from app.main import app
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, delete
from app.models import User, UserCreate, Media
from app import crud


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
        # Clean up Media table
        try:
            media_statement = delete(Media)
            await session.execute(media_statement)
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
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(scope="function")
async def superuser_token_headers(client: httpx.AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    """Superuser authentication headers."""
    # Ensure superuser exists
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = await db_session.execute(statement)
    user = user_result.scalar()
    print(f"Superuser user: {user}")

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=db_session, user_create=user_in)
        print(f"Created superuser: {user}")
    elif not user.is_superuser:
        # Update existing user to be a superuser
        user.is_superuser = True
        user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
        db_session.add(user)
        await db_session.commit()
        print(f"Updated existing user to be superuser: {user}")

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
    tokens = response.json()
    print(f"Tokens: {tokens}")
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def normal_user_token_headers(client: httpx.AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    """Normal user authentication headers."""
    # Ensure normal user exists
    statement = select(User).where(User.email == settings.EMAIL_TEST_USER)
    user_result = await db_session.execute(statement)
    user = user_result.scalar()
    print(f"Normal user: {user}")

    if not user:
        user_in = UserCreate(
            email=settings.EMAIL_TEST_USER,
            password="testpassword123",
        )
        user = crud.create_user(session=db_session, user_create=user_in)
        print(f"Created normal user: {user}")

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.EMAIL_TEST_USER,
            "password": "testpassword123",
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# Add missing import
from app.core.security import get_password_hash