import sentry_sdk
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from sqlmodel import Session, create_engine
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth


from app.api.main import api_router
from app.config import settings
from app.core import db


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
#     sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

print("---------------------")
print(str(settings.SQLALCHEMY_DATABASE_URI))
print("---------------------")

print("--------------****************")
print(settings.API_V1_STR)
print("--------------****************")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# oauth = OAuth(app)
# # oauth = OAuth(config)
# oauth.register(
#     name='google',
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_kwargs={
#         'scope': 'openid email profile'
#     }
# )
# github = oauth.register("github", {...})
# github = oauth.register("github", {...})

# app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


# @app.route("/githublogin")
# def login():
#     redirect_uri = FastAPI.url_path_for("authorize", _external=True)
#     return github.authorize_redirect(redirect_uri)


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

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
with Session(engine) as session:
    db.init_db(session=session)


print("-----------" + route_prefix)

app.include_router(api_router, prefix=route_prefix)
# app.include_router(api_router, prefix="/test")
