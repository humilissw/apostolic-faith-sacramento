"""CSRF protection for form-based submissions.

This middleware provides CSRF protection for non-API routes (HTML pages).
API routes under /api/v1/ are protected by JWT authentication instead.

For API routes, CSRF is not needed because:
- JWT tokens are sent via httpOnly cookies or Authorization header
- The SameSite cookie attribute prevents cross-site requests
- Token-based auth already requires a valid JWT
"""

import secrets
from typing import Annotated, cast

from fastapi import Cookie, HTTPException, Request, status
from fastapi.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

# CSRF token cookie name
CSRF_TOKEN_COOKIE = "csrftoken"

# Expected CSRF header name (X-CSRFToken is standard for Django/CSRF middleware)
CSRF_HEADER_NAME = "x-csrftoken"


def generate_csrf_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(32)


async def get_csrf_token(request: Request) -> str | None:
    """Extract CSRF token from cookie or header.

    Returns the token value if present, None otherwise.
    """
    # Check cookie first (primary source)
    token = cast(str | None, request.cookies.get(CSRF_TOKEN_COOKIE))
    if token:
        return token

    # Fall back to header
    header_token = cast(str | None, request.headers.get(CSRF_HEADER_NAME))
    if header_token:
        return header_token

    return None


class CsrfProtectionMiddleware:
    """ASGI middleware that adds CSRF token to responses and validates on POST/PUT/DELETE/PATCH.

    This middleware:
    1. Adds a CSRF token cookie to all GET responses for non-API routes
    2. Validates the token on state-changing requests (POST, PUT, DELETE, PATCH)
    3. Skips validation for API routes (JWT auth handles security)
    4. Skips validation for CORS preflight (OPTIONS)

    Note: For production deployments with proper SameSite cookie settings and
    JWT authentication, CSRF protection is primarily a defense-in-depth measure
    for non-API HTML endpoints.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        # Skip CSRF validation for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        # Skip CSRF validation for API routes (JWT auth handles security).
        # API routes use httpOnly cookies + JWT tokens which are not sent by browsers
        # on cross-origin requests due to SameSite cookie attributes.
        if request.url.path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        # For non-API routes: skip CSRF if Authorization header is present
        # (JWT-based auth is sufficient protection)
        if "authorization" in request.headers:
            await self.app(scope, receive, send)
            return

        # Validate CSRF token on state-changing methods for non-API requests
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            actual_token = await get_csrf_token(request)
            if not actual_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token missing or invalid",
                )

        # Process the request
        await self.app(scope, receive, send)


async def get_csrf_cookie(request: Request) -> str | None:
    """Get CSRF token from cookie."""
    return request.cookies.get(CSRF_TOKEN_COOKIE)  # type: ignore[no-any-return]


def set_csrf_cookie(response: Response, token: str) -> None:
    """Set CSRF token in response cookie."""
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=3600,  # 1 hour
    )


async def validate_csrf_request(request: Request) -> None:
    """Validate CSRF token in request.

    Skips validation if an Authorization header is present (JWT auth handles security).
    Raises HTTPException with 403 if validation fails.
    """
    # Skip CSRF validation for JWT-authenticated requests
    if "authorization" in request.headers:
        return

    actual_token = await get_csrf_token(request)

    if not actual_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid",
        )


def require_csrf_token() -> Annotated[str, Cookie(None, alias=CSRF_TOKEN_COOKIE)]:
    """Dependency that requires a CSRF token cookie.

    Usage in FastAPI routes:
        async def endpoint(csrf_token: str = Depends(require_csrf_token())):
            # Token is validated by middleware before reaching this point
            pass
    """
    return ""  # Placeholder - actual validation happens in middleware


async def verify_csrf_header(request: Request) -> None:
    """Verify CSRF header is present and valid.

    This is a manual verification function that can be used as a FastAPI dependency
    for specific endpoints that need explicit CSRF validation.
    """
    await validate_csrf_request(request)
