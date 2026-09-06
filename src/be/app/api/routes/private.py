from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    UserCreate,
    UserPublic,
)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    full_name: str
    is_verified: bool = False
    # NOTE: no password field — users set their own password via the
    # one-time signed email link; admins must never set passwords.


@router.post("/users/", response_model=UserPublic)
async def create_user(
    user_in: PrivateUserCreate,
    session: SessionDep,
    _: Any = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new user.

    Requires superuser privileges. The new account is created without a usable
    password; the user receives an email with a one-time link to set it.
    """
    from app.crud import create_user as crud_create_user

    user_create = UserCreate(
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=user_in.is_verified,
    )
    user = await crud_create_user(session=session, user_create=user_create)

    return user
