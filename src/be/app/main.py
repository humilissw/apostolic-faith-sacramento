import asyncio
from os import read

import sentry_sdk
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from sqlmodel import Session, create_engine, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_session,
    async_sessionmaker,
    create_async_engine,
)
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth


from app.api.main import api_router
from app.config import settings
from app.core import db


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


async def setup_db():
    # Initialize database
    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_ASYNC_DATABASE_URI), echo=False, future=True
    )
    async_session_maker = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with AsyncSession(async_engine) as session:
        try:
            from app.models import User, UserCreate
            from app import crud

            statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
            user_result = await session.execute(statement)
            user = user_result.scalar()
            if user is None:
                user_in = UserCreate(
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                )
                user = crud.create_user(session=session, user_create=user_in)
        except Exception as error:
            print(error)
        finally:
            await async_engine.dispose()


async def main_root(app: FastAPI):
    print("---------------------")
    print(str(settings.SQLALCHEMY_DATABASE_URI))
    print("---------------------")

    print("--------------****************")
    print(settings.API_V1_STR)
    print("--------------****************")

    # Set all CORS enabled origins
    # if settings.all_cors_origins:
    #     app.add_middleware(
    #         CORSMiddleware,
    #         allow_origins=settings.all_cors_origins,
    #         allow_credentials=True,
    #         allow_methods=["*"],
    #         allow_headers=["*"],
    #     )

    route_prefix = f"/{settings.API_V1_STR}"

    await setup_db()

    # engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    # with Session(engine) as session:
    #     db.init_db(session=session)

    print("-----------" + route_prefix)

    app.include_router(api_router, prefix=route_prefix)


# if __name__ == "__main__" or __name__ == "app.main":
#     asyncio.run(main_root(app))

# main_root(app)


route_prefix = f"/{settings.API_V1_STR}"
app.include_router(api_router, prefix=route_prefix)
