from sqlmodel import Session, create_engine, select

from app import crud
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from app.models import User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

async def init_db_async(async_engine: AsyncEngine) -> None:
    # # 4. Create an async session maker
    # AsyncSessionLocal = async_sessionmaker(
    #     bind=async_engine,
    #     class_=AsyncSession,
    #     expire_on_commit=False,
    # )
    async with AsyncSession(async_engine) as session:
        statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
        user = await session.execute(statement)
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = crud.create_user(session=session, user_create=user_in)

def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
