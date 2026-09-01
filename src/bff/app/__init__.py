"""AFC Sacramento BFF (Backend-For-Frontend).

A thin Flask layer that sits between the Next.js SPA and the FastAPI backend.
It owns authentication server-side (the browser never sees JWTs) and forwards
``/api/v1/*`` traffic to the upstream API.
"""

__version__ = "0.1.0"
