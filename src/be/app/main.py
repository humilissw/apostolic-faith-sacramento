from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlmodel import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)


from app.api.main import api_router
from app.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


async def main(app: FastAPI):
    print("---------------------")
    print(str(settings.SQLALCHEMY_DATABASE_URI))
    print("---------------------")


async def setup_db():
    # Initialize database
    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_ASYNC_DATABASE_URI), echo=False, future=True
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

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


route_prefix = f"/{settings.API_V1_STR}"
app.include_router(api_router, prefix=route_prefix)
