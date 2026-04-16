from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import select

from app.core import security
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.core.db import get_db_session, SyncSessionLocal
from app.models import TokenPayload, User


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_sync_db_session() -> Session:
    """Synchronous database session for tests."""
    session = SyncSessionLocal()
    yield session
    session.close()


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    header_data = jwt.get_unverified_header(token)

    if header_data["alg"] != security.ALGORITHM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    try:
        payload = jwt.decode(
            token,
            security.PUBLIC_KEY,
            algorithms=[
                header_data["alg"],
            ],
            # algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    statement = select(User).where(User.email == token_data.sub)
    print(statement)
    db_user_result = await session.execute(statement)
    db_user = db_user_result.scalar()
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
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SyncSessionDep = Annotated[Session, Depends(get_sync_db_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
CurrentUser = Annotated[User, Depends(get_current_user)]