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

# Login lockout policy (single source of truth for middleware + route handler).
# Only *failed* credential attempts consume the budget; a successful login
# clears the bucket. See app/api/routes/login.py::login_access_token.
LOGIN_KEY_PREFIX = "login"
LOGIN_MAX_ATTEMPTS = 10
LOGIN_WINDOW_SECONDS = 15 * 60


def login_bucket_key(client_ip: str) -> str:
    return f"{LOGIN_KEY_PREFIX}:{client_ip}"


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, respecting X-Forwarded-For if behind a proxy.

    All rate-limit call sites (middleware *and* route handlers) must use this
    helper. Using ``request.client.host`` directly collapses every user behind
    a reverse proxy / Docker network into one shared bucket, which makes the
    limits wildly aggressive in production.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return str(forwarded.split(",")[0].strip())
    return request.client.host if request.client else "unknown"


# Backward-compatible private alias (used by older imports/tests)
_get_client_ip = get_client_ip


def _check_rate_limit(
    key: str, max_requests: int, window_seconds: int, consume: bool = True
) -> bool:
    """Check if the request is within the rate limit.

    Returns True if the request is allowed, False if rate-limited.

    ``consume=True`` (default) records this request against the bucket.
    ``consume=False`` only inspects the bucket without recording — use it to
    reject already-locked-out clients while leaving policy decisions (e.g.
    "only count *failed* attempts") to the caller.
    """
    now = time.time()
    window_start = now - window_seconds

    # Prune old entries
    _requests[key] = [t for t in _requests[key] if t > window_start]

    if len(_requests[key]) >= max_requests:
        return False

    if consume:
        _requests[key].append(now)
    return True


def reset_rate_bucket(key: str) -> None:
    """Clear a single rate-limit bucket (e.g. after a successful login)."""
    _requests.pop(key, None)


def retry_after_seconds(key: str, window_seconds: int) -> int:
    """Seconds until the oldest entry in ``key``'s window expires (0 if none)."""
    now = time.time()
    window_start = now - window_seconds
    timestamps = sorted(t for t in _requests.get(key, []) if t > window_start)
    if not timestamps:
        return 0
    return max(1, int(window_start + window_seconds - timestamps[0]) + 1)


class RateLimitMiddleware:
    """ASGI middleware that enforces rate limits on API endpoints.

    Default limits (per client IP, resolved via X-Forwarded-For when proxied):
    - All API routes: 100 requests per minute
    - Login / signup: NOT consumed here — enforced per-endpoint, where the
      handler can distinguish successful logins from failed ones. The
      middleware only enforces the resulting lockout (non-consuming check)
      so a locked-out client never reaches the route logic.
    - Token refresh: 60 requests per 5 minutes (token refresh is a normal,
      frequent client operation — especially with multiple tabs open).

    Limits are applied per-IP and persist for the lifetime of the process.
    For production, consider using a distributed rate limiter (Redis-backed).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def _reject(self, scope: Scope, receive: Receive, send: Send, retry_after: int = 0):
        response = Response(
            content='{"detail":"Rate limit exceeded. Please try again later."}',
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/json",
            headers={"retry-after": str(max(1, retry_after))},
        )
        await response(scope, receive, send)

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

        # CORS preflight requests do nothing server-side; don't burn budget.
        if request.method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        client_ip = _get_client_ip(request)

        # Login lockout: enforce only — the route handler decides what counts
        # (failed credential attempts). Never consume a slot here, or every
        # *successful* login would eat into the user's allowance.
        if "login/access-token" in request.url.path:
            key = login_bucket_key(client_ip)
            if not _check_rate_limit(
                key, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS, consume=False
            ):
                await self._reject(scope, receive, send, retry_after_seconds(key, LOGIN_WINDOW_SECONDS))
                return

        # Check token refresh limits
        if "login/refresh-token" in request.url.path:
            key = f"refresh:{client_ip}"
            if not _check_rate_limit(key, 60, 5 * 60):
                await self._reject(scope, receive, send, retry_after_seconds(key, 5 * 60))
                return

        # Default rate limit for all other API routes: 100 req/min per IP
        if not _check_rate_limit(f"api:{client_ip}", 100, 60):
            await self._reject(scope, receive, send, retry_after_seconds(f"api:{client_ip}", 60))
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
