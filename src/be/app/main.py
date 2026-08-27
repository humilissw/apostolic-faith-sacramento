from pathlib import Path
import traceback

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.api.deps import oauth2_scheme
from app.core.scopes import Scope
from app.core.csrf import CsrfProtectionMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.rate_limiter import RateLimitMiddleware
from app.config import settings


def _run_migrations_on_startup() -> None:
    """Run `alembic upgrade head` once on startup (dev convenience).

    Serialized across uvicorn workers with an exclusive file lock, and retried
    briefly in case the database container is still booting.
    """
    import fcntl
    import time

    from alembic import command
    from alembic.config import Config as AlembicConfig

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    lock_path = Path("/tmp/afc_alembic_startup.lock")

    with lock_path.open("w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        for attempt in range(1, 31):
            try:
                command.upgrade(AlembicConfig(str(alembic_ini)), "head")
                break
            except Exception as exc:  # noqa: BLE001 - dev convenience, log and give up
                if attempt == 30:
                    print(f"RUN_MIGRATIONS_ON_STARTUP failed after {attempt} attempts: {exc}")
                else:
                    time.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.RUN_MIGRATIONS_ON_STARTUP:
        _run_migrations_on_startup()
    yield


def parse_cors_origins(cors_origins_str: str) -> list[str]:
    """Parse CORS origins from settings string into a list.

    Accepts comma-separated values or JSON array format.
    Falls back to safe defaults if parsing fails.
    """
    cors_origins_str = cors_origins_str.strip()
    if not cors_origins_str:
        return []

    # Try parsing as JSON array first
    if cors_origins_str.startswith("["):
        import json

        try:
            parsed_origins = json.loads(cors_origins_str)
            if isinstance(parsed_origins, list):
                return [str(o).strip() for o in parsed_origins if o]
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback to comma-separated parsing
    return [str(o).strip() for o in cors_origins_str.split(",") if o.strip()]


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

try:
    # Parse CORS origins from settings (not hardcoded list)
    cors_origins = parse_cors_origins(settings.BACKEND_CORS_ORIGINS)

    # If no origins configured in settings, use safe defaults for development
    if not cors_origins:
        cors_origins = [
            "http://localhost.tiangolo.com",
            "https://localhost.tiangolo.com",
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:3000",
            "https://localhost:3000",
        ]

    print("**********Starting app...**********")
    print(f"CORS origins configured: {len(cors_origins)}")
    for origin in cors_origins:
        print(f"  - {origin}")
    print(f"***** Route Path: {settings.API_V1_STR} *****")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # OAuth2 scope definitions for OpenAPI/Swagger UI
    app.security_schemes = {
        "OAuth2PasswordBearer": oauth2_scheme,
    }
    app.security = [{"OAuth2PasswordBearer": [s.value for s in Scope]}]

    # Add rate limiting middleware (before routes)
    app.add_middleware(RateLimitMiddleware)

    # Add CSRF protection middleware (before routes)
    app.add_middleware(CsrfProtectionMiddleware)

    # Add security headers middleware (pass environment for HSTS control)
    app.add_middleware(SecurityHeadersMiddleware, env=settings.ENVIRONMENT)

    app.include_router(api_router, prefix=settings.API_V1_STR)

    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

    @app.get("/", response_class=HTMLResponse)
    def read_root(request: Request):
        return templates.TemplateResponse(request, "index.html")

    handler = app

    if __name__ == "__main__":
        import uvicorn

        uvicorn.run("app.main:app", host="0.0.0.0", port=5001, reload=True)

except Exception:
    print(traceback.format_exc())
    exit(-1)
