"""ASGI middleware for broad API rate limiting.

Protects all API endpoints from brute-force and abuse by enforcing per-IP
rate limits. Uses a sliding-window algorithm with in-memory storage.

For production deployments behind a reverse proxy (nginx, Cloudflare), prefer
proxy-level rate limiting. This is a fallback for single-server or development
deployments.
"""

import time
from collections import defaultdict

from fastapi import Request, Response, status
from starlette.types import ASGIApp, Receive, Scope, Send

# Global rate limit state
_requests: dict[str, list[float]] = defaultdict(list)


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, respecting X-Forwarded-For if behind a proxy."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return str(forwarded.split(",")[0].strip())
    return request.client.host if request.client else "unknown"


def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """Check if the request is within the rate limit.

    Returns True if the request is allowed, False if rate-limited.
    """
    now = time.time()
    window_start = now - window_seconds

    # Prune old entries
    _requests[key] = [t for t in _requests[key] if t > window_start]

    if len(_requests[key]) >= max_requests:
        return False

    _requests[key].append(now)
    return True


class RateLimitMiddleware:
    """ASGI middleware that enforces rate limits on API endpoints.

    Default limits (per IP):
    - All API routes: 100 requests per minute
    - Login endpoints: 5 requests per 15 minutes (already handled per-endpoint)
    - Signup endpoint: 5 requests per 15 minutes (already handled per-endpoint)
    - Token refresh: 10 requests per 5 minutes

    Limits are applied per-IP and persist for the lifetime of the process.
    For production, consider using a distributed rate limiter (Redis-backed).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        # Only apply to API routes
        if not request.url.path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        # Skip rate limiting for health/liveness probes
        if any(request.url.path.endswith(p) for p in ["/liveness", "/readiness", "/health"]):
            await self.app(scope, receive, send)
            return

        client_ip = _get_client_ip(request)

        # Check login-specific limits (already enforced per-endpoint, but double-check)
        if "login/access-token" in request.url.path:
            if not _check_rate_limit(f"login:{client_ip}", 5, 15 * 60):
                response = Response(
                    content='{"detail":"Rate limit exceeded. Please try again later."}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                )
                await response(scope, receive, send)
                return

        # Check token refresh limits
        if "login/refresh-token" in request.url.path:
            if not _check_rate_limit(f"refresh:{client_ip}", 10, 5 * 60):
                response = Response(
                    content='{"detail":"Rate limit exceeded. Please try again later."}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                )
                await response(scope, receive, send)
                return

        # Check signup limits (already enforced per-endpoint, but double-check)
        if "signup" in request.url.path:
            if not _check_rate_limit(f"signup:{client_ip}", 5, 15 * 60):
                response = Response(
                    content='{"detail":"Rate limit exceeded. Please try again later."}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                )
                await response(scope, receive, send)
                return

        # Default rate limit for all other API routes: 100 req/min per IP
        if not _check_rate_limit(f"api:{client_ip}", 100, 60):
            response = Response(
                content='{"detail":"Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
            )
            await response(scope, receive, send)
            return

        # Process the request
        await self.app(scope, receive, send)


def reset_all_rate_limits() -> None:
    """Clear all rate limiter state. Useful for tests."""
    _requests.clear()


# Backward-compatible aliases for existing test imports
reset_rate_limit = reset_all_rate_limits

# Public alias for use in route handlers
check_rate_limit = _check_rate_limit
