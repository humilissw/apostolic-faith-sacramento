from sqlmodel import create_engine, select

from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import *

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# Sync database session for tests
SyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

# Dependency to inject the async database session
async def get_db_session() -> AsyncSession:
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


async def init_db_async() -> None:
    """Initialize database - creates superuser if it doesn't exist."""
    # Get the async session maker (this will create the engine if it doesn't exist)
    async_session_maker = get_db_session()

    async with async_session_maker as session:
        try:
            from app.models import User, UserCreate
            from app import crud

            statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
            user_result = await session.execute(statement)
            user = user_result.scalar()
            print("==============")
            print(user)
            print(user.email)
            print("==============")
            if user is None:
                user_in = UserCreate(
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                )
                user = crud.create_user(session=session, user_create=user_in)
        except Exception as error:
            print(error)