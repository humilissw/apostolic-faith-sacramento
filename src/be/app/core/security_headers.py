"""Security headers middleware for FastAPI."""

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """ASGI middleware that adds security headers to all responses.

    Sets:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: camera=(), microphone=(), geolocation=()
    - Content-Security-Policy: restricts resource loading to same-origin + trusted sources
    - Strict-Transport-Security: enforces HTTPS (only in production)

    CSP is set here as a baseline; the frontend may override with more specific policies.

    IMPORTANT: This middleware preserves duplicate headers (like Set-Cookie)
    by operating on the raw header list instead of converting to a dict.
    """

    def __init__(self, app: ASGIApp, env: str = "production") -> None:
        self.app = app
        self.env = env

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message["headers"])  # Copy to avoid mutation issues

                # Remove Server header (first occurrence only)
                headers = [(k, v) for k, v in headers if k.lower() != b"server"]

                # Add security headers -- these won't conflict with Set-Cookie duplicates
                security_headers: list[tuple[bytes, bytes]] = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                    # Content-Security-Policy: baseline policy for API and static assets
                    (
                        b"content-security-policy",
                        b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                        b"img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; "
                        b"frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
                    ),
                ]

                # Add HSTS in production only
                if self.env.lower() in ("production", "prod", "live"):
                    security_headers.append(
                        (
                            b"strict-transport-security",
                            b"max-age=31536000; includeSubDomains; preload",
                        )
                    )

                # Only add headers that don't already exist (by lowercase key)
                existing_keys = {k.lower() for k, v in headers}
                for key, value in security_headers:
                    if key not in existing_keys:
                        headers.append((key, value))

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_wrapper)
