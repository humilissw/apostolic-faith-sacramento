from sqlalchemy import Row
from sqlmodel import create_engine, select

from app import crud
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from app.models import *

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
async_engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False, # Recommended for async use
    class_=AsyncSession,
)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

# Dependency to inject the async database session
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db_async(async_engine: AsyncEngine) -> None:
    # # 4. Create an async session maker
    # AsyncSessionLocal = async_sessionmaker(
    #     bind=async_engine,
    #     class_=AsyncSession,
    #     expire_on_commit=False,
    # )
    async with AsyncSession(async_engine) as session:
        try:            
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

async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = await session.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.create_user(session=session, user_create=user_in)
