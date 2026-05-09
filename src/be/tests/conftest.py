import sys
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport
import httpx

from app.config import settings
from app.main import app
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, delete
from app.models import (
    Assignment,
    User,
    UserCreate,
    UserScope,
    Media,
    VideoUpload,
    ClientCredentials,
    IntegrationConfig,
    Payment,
    DonationConfig,
    RefreshToken,
    AuthorizationCode,
)
from app import crud


# Fake google module for tests (google-auth is not a project dependency)
# verify_id_token must return a 2-tuple (credentials, payload) directly, not another MagicMock
def _fake_verify_id_token(id_token, client_id=None):
    return (MagicMock(), {"email": "test@example.com", "email_verified": True})


_google_auth_jwt = MagicMock()
_google_auth_jwt.verify_id_token = _fake_verify_id_token
_google_auth_pkg = MagicMock()
_google_auth_pkg.jwt = _google_auth_jwt
_google_pkg = MagicMock()
_google_pkg.auth = _google_auth_pkg
sys.modules.setdefault("google", _google_pkg)
sys.modules.setdefault("google.auth", _google_auth_pkg)
sys.modules.setdefault("google.auth.jwt", _google_auth_jwt)


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test."""
    loop = pytest.plugins.asyncio._get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Function-scoped database session for individual tests."""
    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_ASYNC_DATABASE_URI), echo=False, future=True
    )

    # Create all tables (including new ones like authorization_codes)
    from sqlmodel import SQLModel

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    session = async_session_maker()

    try:
        try:
            for model in [
                Assignment,
                RefreshToken,
                AuthorizationCode,
                ClientCredentials,
                IntegrationConfig,
                Payment,
                DonationConfig,
                VideoUpload,
                Media,
            ]:
                await session.execute(delete(model))
            await session.commit()
        except Exception:
            await session.rollback()

        # Ensure FIRST_SUPERUSER exists in the test database
        from app.core.security import get_password_hash, verify_password

        stmt = select(User).where(User.email == settings.FIRST_SUPERUSER)
        user_result = await session.execute(stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_active=True,
                is_superuser=True,
            )
            await crud.create_user(session=session, user_create=user_in)
        else:
            if not verify_password(settings.FIRST_SUPERUSER_PASSWORD, user.hashed_password):
                user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
                user.is_superuser = True
                session.add(user)
                await session.commit()

        from app.core.rate_limiter import reset_rate_limit

        reset_rate_limit()

        yield session
    finally:
        await session.close()
        await async_engine.dispose()


@pytest.fixture(scope="function")
async def client() -> httpx.AsyncClient:
    """Function-scoped async test client for ASGI app."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(scope="function")
async def superuser_token_headers(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> dict[str, str]:
    """Superuser authentication headers."""
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = await db_session.execute(statement)
    user = user_result.scalar()

    from app.core.security import get_password_hash

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.create_user(session=db_session, user_create=user_in)
    else:
        user.is_superuser = True
        user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
        db_session.add(user)
        await db_session.commit()
        # Ensure superuser scope is seeded (for scope-based auth)
        from app.models import UserScope

        has_scope = await db_session.execute(
            select(UserScope).where(
                UserScope.user_id == user.id,  # type: ignore[arg-type]
                UserScope.scope == "superuser",  # type: ignore[arg-type]
            )
        )
        if not has_scope.scalar_one_or_none():
            db_session.add(UserScope(user_id=user.id, scope="superuser"))
            await db_session.commit()

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
async def normal_user_token_headers(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> dict[str, str]:
    """Normal user authentication headers with api:all scope."""
    statement = select(User).where(User.email == settings.EMAIL_TEST_USER)
    user_result = await db_session.execute(statement)
    user = user_result.scalar()

    if not user:
        user_in = UserCreate(
            email=settings.EMAIL_TEST_USER,
            password="testpassword123",
        )
        user = await crud.create_user(session=db_session, user_create=user_in)
    else:
        from app.core.security import get_password_hash

        user.hashed_password = get_password_hash("testpassword123")
        db_session.add(user)
        await db_session.commit()

    # Grant api:all so normal tests can exercise API endpoints
    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "api:all")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="api:all"))
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.EMAIL_TEST_USER,
            "password": "testpassword123",
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
