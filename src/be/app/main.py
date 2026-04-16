import asyncio
from os import read

import sentry_sdk
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_session, async_sessionmaker, create_async_engine
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth


from app.api.main import api_router
from app.config import settings
from app.core import db

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

async def setup_db():
    await db.init_db_async(async_engine)

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

# engine = create_async_engine(env.DATABASE_URL, echo=True)
eg = db.async_engine
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

local = db.AsyncSessionLocal

print(__name__)
main_root(app)
# read(1, 1)
# if __name__ == "__main__" or __name__ == "app.main":
#     asyncio.run(main_root(app)) # Runs the main coroutine and manages the event loop

