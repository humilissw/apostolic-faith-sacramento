from typing import Annotated, Callable, Generator

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.openapi.models import OAuthFlowPassword, OAuthFlows
from fastapi.security import OAuth2, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import select

from app.core import security
from app.core.scopes import Scope
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.models import TokenPayload, User
from app.core.db import SyncSessionLocal, get_db_session


async def get_token_from_cookie(request: Request) -> str | None:
    """Extract access token from httpOnly cookie, if present."""
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    return str(token) if token else None  # type: ignore[no-any-return]


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

# OAuth2 security scheme with scopes for OpenAPI/Swagger UI
oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        password=OAuthFlowPassword(
            tokenUrl=f"{settings.API_V1_STR}/login/access-token",
            scopes={s.value: s.value for s in Scope},
        )
    )
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_sync_db_session() -> Generator[Session]:
    """Synchronous database session for tests."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


SyncSessionDep = Annotated[Session, Depends(get_sync_db_session)]


async def get_current_user(
    session: SessionDep,
    token: TokenDep,
    request: Request,
) -> User:
    """Validate JWT token and return the current user.

    Checks the httpOnly cookie first (primary), then falls back to
    the Authorization header (backwards compat for Swagger/UI and
    any clients that still send Bearer tokens).
    """
    cookie_token = await get_token_from_cookie(request)
    token_to_use = cookie_token or token

    try:
        payload = jwt.decode(
            token_to_use,
            security.PUBLIC_KEY,
            algorithms=[security.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    statement = select(User).where(User.email == token_data.sub)
    db_user_result = await session.execute(statement)
    db_user = db_user_result.scalar()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = await session.get(User, db_user.id)  # type: ignore[arg-type]

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user  # type: ignore[no-any-return]


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user


async def get_current_user_with_scopes(
    session: SessionDep,
    request: Request,
    token: str = Depends(reusable_oauth2),
) -> tuple[User, list[str]]:
    """Validate JWT token and return (user, scopes) tuple."""
    cookie_token = await get_token_from_cookie(request)
    # Fall back to Authorization header token
    auth_header = request.headers.get("authorization", "")
    header_token = None
    if auth_header.startswith("Bearer "):
        header_token = auth_header[7:]
    token_to_use = cookie_token or header_token or token

    try:
        payload = jwt.decode(
            token_to_use,
            security.PUBLIC_KEY,
            algorithms=[security.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    statement = select(User).where(User.email == token_data.sub)
    db_user_result = await session.execute(statement)
    db_user = db_user_result.scalar()  # type: ignore[assignment]
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = await session.get(User, db_user.id)  # type: ignore[arg-type]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    scopes = token_data.scopes or []
    return user, scopes


async def _get_user_scopes(session: AsyncSession, user: User) -> list[str]:
    """Get scopes for a user from DB, falling back to token scopes."""
    from app.repositories.user_scope_repo import UserScopeRepository

    repo = UserScopeRepository(session)
    db_scopes = await repo.get_scopes(user.id)
    if db_scopes:
        return ["api:all"] if "api:all" in db_scopes else db_scopes
    # Fall back to a default set of scopes for backward compat
    return []


async def get_current_active_superuser_bypass(
    session: SessionDep,
    request: Request,
) -> User:
    """Authenticate user and return them, without requiring superuser status."""
    cookie_token = await get_token_from_cookie(request)
    auth_header = request.headers.get("authorization", "")
    header_token = None
    if auth_header.startswith("Bearer "):
        header_token = auth_header[7:]
    token_to_use = cookie_token or header_token
    try:
        payload = jwt.decode(
            token_to_use,
            security.PUBLIC_KEY,
            algorithms=[security.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    statement = select(User).where(User.email == token_data.sub)
    db_user_result = await session.execute(statement)
    db_user = db_user_result.scalar()  # type: ignore[assignment]
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = await session.get(User, db_user.id)  # type: ignore[arg-type]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def require_scope(required_scope: str) -> Callable:
    """Return a dependency that checks if the user has the required scope.

    Superusers bypass scope checks entirely.
    """

    async def scope_checker(
        user_scopes: Annotated[tuple[User, list[str]], Depends(get_current_user_with_scopes)],
    ) -> User:
        user, scopes = user_scopes
        if user.is_superuser:
            return user
        if required_scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {required_scope}",
            )
        return user

    return Depends(scope_checker)  # type: ignore[no-any-return]


def require_any_scope(required_scopes: list[str]) -> Callable:
    """Return a dependency that checks if the user has any of the required scopes."""

    async def scope_checker(
        user_scopes: Annotated[tuple[User, list[str]], Depends(get_current_user_with_scopes)],
    ) -> User:
        user, scopes = user_scopes
        if user.is_superuser:
            return user
        if not any(s in scopes for s in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope(s): {', '.join(required_scopes)}",
            )
        return user

    return Depends(scope_checker)  # type: ignore[no-any-return]
