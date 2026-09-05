from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    require_scope,
)
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    validate_password_complexity,
)
from app import crud
from app.repositories.user_repo import UserRepository
from app.repositories.user_scope_repo import UserScopeRepository
from app.services.user_management_service import UserManagementService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


async def _populate_scopes(session: AsyncSession, user: User) -> UserPublic:
    """Return a UserPublic with assigned_scopes populated."""
    repo = UserScopeRepository(session)
    scopes = await repo.get_scopes(user.id)
    return UserPublic(
        email=user.email,
        is_active=user.is_active,
        id=user.id,
        new_id=user.new_id,
        full_name=user.full_name,
        assigned_scopes=scopes,
    )


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    repository = UserRepository(session=session)
    users, total_count = await repository.get_all(skip=skip, limit=limit)
    populated = [await _populate_scopes(session, u) for u in users]
    return UsersPublic(data=populated, count=total_count)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.

    Password must meet complexity requirements. Admin-created users are exempt from
    scope assignment.
    """
    svc = UserManagementService(session)
    try:
        return await svc.create_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/me",
    response_model=UserPublic,
)
async def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    svc = UserManagementService(session)
    try:
        return await svc.update_user_me(current_user, user_in)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch(
    "/me/password",
    response_model=Message,
)
async def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    svc = UserManagementService(session)
    try:
        return await svc.update_password_me(current_user, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/me",
    response_model=UserPublic,
)
async def read_user_me(current_user: CurrentUser, session: SessionDep) -> Any:
    """
    Get current user.
    """
    return await _populate_scopes(session, current_user)


@router.delete(
    "/me",
    response_model=Message,
)
async def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    svc = UserManagementService(session)
    try:
        return await svc.delete_user_me(current_user)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/signup", response_model=UserPublic)
async def register_user(
    *,
    request: Request,
    session: SessionDep,
    user_in: UserRegister,
) -> Any:
    """
    Create new user without the need to be logged in.

    Rate limited to prevent account spamming (5 requests per 15 minutes per IP).
    Password must meet complexity requirements.
    """
    from app.core.rate_limiter import check_rate_limit, get_client_ip

    ip = get_client_ip(request)
    if not check_rate_limit(f"signup:{ip}", 5, 15 * 60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    if not validate_password_complexity(user_in.password):
        raise HTTPException(
            status_code=400,
            detail=(
                "Password must be at least 8 characters and contain uppercase, "
                "lowercase, digit, and special character."
            ),
        )

    user = await crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = await crud.create_user(session=session, user_create=user_create)
    return user


@router.get(
    "/admin/{user_id}/scopes",
    dependencies=[Depends(get_current_active_superuser)],
)
async def get_user_scopes(user_id: str, session: SessionDep) -> list[str]:
    """
    Get scopes assigned to a user.
    """
    repo = UserScopeRepository(session)
    return await repo.get_scopes(user_id)


@router.put(
    "/admin/{user_id}/scopes",
    dependencies=[Depends(get_current_active_superuser)],
)
async def set_user_scopes(user_id: str, scopes: list[str], session: SessionDep) -> list[str]:
    """
    Set scopes for a user, replacing existing ones.
    """
    repo = UserScopeRepository(session)
    await repo.set_scopes(user_id, scopes)
    return await repo.get_scopes(user_id)


@router.delete(
    "/admin/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
async def remove_user_scopes(user_id: str, session: SessionDep, response: Response) -> None:
    """
    Remove all scopes from a user (does not delete the user).
    """
    repo = UserScopeRepository(session)
    await repo.set_scopes(user_id, [])
    response.status_code = 204


@router.post(
    "/admin/bulk-delete",
    dependencies=[Depends(get_current_active_superuser)],
)
async def bulk_delete_users(session: SessionDep, user_ids: list[str] = Body(...)) -> Message:
    """Delete multiple users and their associated data."""
    svc = UserManagementService(session)
    return await svc.bulk_delete_users(user_ids)


@router.get(
    "/admin/all",
    dependencies=[require_scope("scheduler:admin")],
    response_model=UsersPublic,
)
async def get_all_users(session: SessionDep) -> Any:
    """Get all users without pagination (scheduler:admin scope required)."""
    repository = UserRepository(session=session)
    users, _ = await repository.get_all(skip=0, limit=10000)
    populated = [await _populate_scopes(session, u) for u in users]
    return UsersPublic(data=populated, count=len(populated))


@router.get(
    "/{user_id}",
    response_model=UserPublic,
)
async def read_user_by_id(user_id: str, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get a specific user by id.
    """
    repository = UserRepository(session=session)
    user = await repository.get_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        return await _populate_scopes(session, user)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return await _populate_scopes(session, user)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    *,
    session: SessionDep,
    user_id: str,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    svc = UserManagementService(session)
    try:
        return await svc.update_user(user_id, user_in)
    except ValueError as e:
        if "email" in str(e).lower() and (
            "exists" in str(e).lower() or "already" in str(e).lower()
        ):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(session: SessionDep, current_user: CurrentUser, user_id: str) -> Message:
    """
    Delete a user.
    """
    svc = UserManagementService(session)
    try:
        return await svc.delete_user(user_id, current_user)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=403, detail=str(e))
