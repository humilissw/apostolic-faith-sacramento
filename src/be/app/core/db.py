from typing import Any

from sqlalchemy.orm import Session

from sqlmodel import create_engine, select

from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import User  # noqa: F403

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# Sync database session for tests
SyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# Async database session for production use
async_engine = create_async_engine(
    str(settings.SQLALCHEMY_ASYNC_DATABASE_URI), echo=False, future=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


# Dependency to inject the async database session
async def get_db_session() -> Any:
    """Create a new async database session for each request."""
    # Create a new async engine for each request to avoid event loop issues
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
        yield session
    finally:
        await session.close()
        await async_engine.dispose()


# Sync database session for tests
def get_sync_db_session():
    """Synchronous database session for tests."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_async_session():
    """Async database session for pre-start checks."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


async def init_db_async() -> None:
    """Initialize database - creates superuser if it doesn't exist."""
    session = AsyncSessionLocal()
    try:
        from app.models import User, UserCreate, UserScope
        from app import crud

        statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
        user_result = await session.execute(statement)
        user = user_result.scalar()
        print("==============")
        print(user)
        if user is not None:
            print(user.email)
        print("==============")
        if user is None:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = await crud.create_user(session=session, user_create=user_in)
            # Seed superuser scope
            session.add(UserScope(user_id=user.id, scope="superuser"))
            await session.commit()
    except Exception as error:
        print(error)
    finally:
        await session.close()


def init_db(session: Session) -> None:
    """Initialize database - creates superuser if it doesn't exist (sync version)."""
    from app.models import UserCreate, UserScope

    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_result = session.execute(statement)
    user = user_result.scalar()
    if user is None:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        db_user = User.model_validate(user_in, update={"hashed_password": ""})
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        # Seed superuser scope
        session.add(UserScope(user_id=db_user.id, scope="superuser"))
        session.commit()
