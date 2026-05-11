"""OAuth2 scopes for JWT token claims."""

from enum import Enum


class Scope(str, Enum):
    # Core access scopes
    API_ALL = "api:all"
    SPA_ALL = "spa:all"
    MOBILE_ALL = "mobile:all"
    PUBLIC_READ = "public:read"

    # Payment scopes
    PAYMENTS_READ = "payments:read"
    PAYMENTS_WRITE = "payments:write"
    PAYMENTS_ADMIN = "payments:admin"

    # Integration scopes
    INTEGRATIONS_ADMIN = "integrations:admin"

    # Video upload scopes
    VIDEO_UPLOADS_READ = "video_uploads:read"
    VIDEO_UPLOADS_WRITE = "video_uploads:write"
    VIDEO_UPLOADS_DELETE = "video_uploads:delete"
    VIDEO_UPLOADS_MANAGE = "video_uploads:manage"

    # User management scopes
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_ADMIN = "users:admin"

    # Scheduler scopes
    SCHEDULER_ADMIN = "scheduler:admin"
    MEMBER_LIMITED = "member:limited"

    # Superuser claim (replaces is_superuser boolean)
    SUPERUSER = "superuser"
    # Service-to-service auth
    CLIENT = "client"
