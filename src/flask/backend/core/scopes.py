"""OAuth2 scopes for JWT token claims."""

from enum import Enum


class Scope(str, Enum):
    API_ALL = "api:all"
    SPA_ALL = "spa:all"
    MOBILE_ALL = "mobile:all"
    PUBLIC_READ = "public:read"
    PAYMENTS_READ = "payments:read"
    PAYMENTS_WRITE = "payments:write"
    PAYMENTS_ADMIN = "payments:admin"
    INTEGRATIONS_ADMIN = "integrations:admin"
    VIDEO_UPLOADS_READ = "video_uploads:read"
    VIDEO_UPLOADS_WRITE = "video_uploads:write"
    VIDEO_UPLOADS_DELETE = "video_uploads:delete"
    VIDEO_UPLOADS_MANAGE = "video_uploads:manage"
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_ADMIN = "users:admin"
    SCHEDULER_ADMIN = "scheduler:admin"
    MEMBER_LIMITED = "member:limited"
    SUPERUSER = "superuser"
    CLIENT = "client"
