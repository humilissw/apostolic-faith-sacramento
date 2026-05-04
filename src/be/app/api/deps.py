from typing import Annotated, Callable, Generator

import jwt
from fastapi import Depends, HTTPException, status
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


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Validate JWT token and return the current user.

    Security fixes:
    - Hardcodes RS256 algorithm to prevent algorithm confusion attacks
    - Verifies iss and aud claims to prevent token confusion across services
    """
    try:
        payload = jwt.decode(
            token,
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
    user = await session.get(User, db_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


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
    session: SessionDep, token: TokenDep
) -> tuple[User, list[str]]:
    """Validate JWT token and return (user, scopes) tuple."""
    try:
        payload = jwt.decode(
            token,
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
