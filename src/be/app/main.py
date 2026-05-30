from pathlib import Path
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.main import api_router
from app.api.deps import oauth2_scheme
from app.core.scopes import Scope
from app.config import settings

print("**********Starting app...**********")
print(
    "********--------App Settings loaded: "
    + str((settings.BACKEND_CORS_ORIGINS is not None and settings.BACKEND_CORS_ORIGINS != ""))
)
print("***** Route Path: " + settings.API_V1_STR)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://localhost:3000",
    "https://qa.afcsacramento.org",
    "https://pre.afcsacramento.org",
    "https://afcsacramento.org",
    "https://www.afcsacramento.org",
    "https://www.pre.afcsacramento.org",
]


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # generate_unique_id_function=custom_generate_unique_id,
)

try:
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["*"],
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # OAuth2 scope definitions for OpenAPI/Swagger UI
    app.security_schemes = {
        "OAuth2PasswordBearer": oauth2_scheme,
    }
    app.security = [{"OAuth2PasswordBearer": [s.value for s in Scope]}]

    app.include_router(api_router, prefix=settings.API_V1_STR)

    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

    @app.get("/", response_class=HTMLResponse)
    def read_root(request: Request):
        return templates.TemplateResponse(request, "index.html")

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)

except Exception:
    print(traceback.format_exc())
    exit(-1)
