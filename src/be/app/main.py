import asyncio

import sentry_sdk
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth


from app.api.main import api_router
from app.config import settings
from app.core import db

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

async def main(app: FastAPI):
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

    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True
    )

    await db.init_db_async(async_engine)

    # engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    # with Session(engine) as session:
    #     db.init_db(session=session)


    print("-----------" + route_prefix)

    app.include_router(api_router, prefix=route_prefix)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

if __name__ == "__main__":
    asyncio.run(main(app)) # Runs the main coroutine and manages the event loop

