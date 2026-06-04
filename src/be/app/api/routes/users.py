from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    require_scope,
)
from app.config import settings
from app.core.security import verify_password, get_password_hash
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UserScope,
)
from app import crud
from app.repositories.user_repo import UserRepository
from app.repositories.user_scope_repo import UserScopeRepository
from app.utils import generate_new_account_email, send_email

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
    """
    repository = UserRepository(session=session)
    user = await repository.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = await repository.create(user_create=user_in)
    if user_in.scopes:
        scope_repo = UserScopeRepository(session)
        await scope_repo.set_scopes(user.id, user_in.scopes)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return await _populate_scopes(session, user)


@router.patch(
    "/me",
    response_model=UserPublic,
    dependencies=[require_scope("api:all")],
)
async def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    repository = UserRepository(session=session)

    if user_in.email:
        existing_user = await repository.get_by_email(email=user_in.email)
        if existing_user and existing_user.new_id != current_user.new_id:
            raise HTTPException(status_code=409, detail="User with this email already exists")
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.patch(
    "/me/password",
    response_model=Message,
    dependencies=[require_scope("api:all")],
)
async def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    await session.commit()
    return Message(message="Password updated successfully")


@router.get(
    "/me",
    response_model=UserPublic,
    dependencies=[require_scope("api:all")],
)
async def read_user_me(current_user: CurrentUser, session: SessionDep) -> Any:
    """
    Get current user.
    """
    return await _populate_scopes(session, current_user)


@router.delete(
    "/me",
    response_model=Message,
    dependencies=[require_scope("api:all")],
)
async def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    user_id = str(current_user.id)
    scopes_stmt = delete(UserScope).where(UserScope.user_id == user_id)  # type: ignore[arg-type]
    await session.execute(scopes_stmt)
    await session.delete(current_user)
    await session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
async def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
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
    deleted = 0
    for uid in user_ids:
        user = await UserRepository(session).get_by_id(uid)
        if user:
            user_id_str = str(user.id)
            items_stmt = delete(Item).where(Item.owner_id == user.id)  # type: ignore[arg-type]
            await session.execute(items_stmt)
            scopes_stmt = delete(UserScope).where(
                UserScope.user_id == user_id_str  # type: ignore[arg-type]
            )
            await session.execute(scopes_stmt)
            await session.delete(user)
            deleted += 1
    await session.commit()
    return Message(message=f"Deleted {deleted} users")


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
    dependencies=[require_scope("api:all")],
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
    repository = UserRepository(session=session)
    db_user = await repository.get_by_id(user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = await repository.get_by_email(email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="User with this email already exists")

    db_user = await repository.update(db_user=db_user, user_in=user_in)
    return await _populate_scopes(session, db_user)


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(session: SessionDep, current_user: CurrentUser, user_id: str) -> Message:
    """
    Delete a user.
    """
    repository = UserRepository(session=session)
    user = await repository.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    user_id_str = str(user.id)
    items_stmt = delete(Item).where(Item.owner_id == user_id)  # type: ignore[arg-type]
    await session.execute(items_stmt)  # type: ignore
    scopes_stmt = delete(UserScope).where(
        UserScope.user_id == user_id_str  # type: ignore[arg-type]
    )
    await session.execute(scopes_stmt)
    await session.delete(user)
    await session.commit()
    return Message(message="User deleted successfully")
