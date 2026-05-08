"""Routes for managing per-user scopes (claims)."""

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import User
from app.repositories.user_scope_repo import UserScopeRepository

router = APIRouter(prefix="/users/admin", tags=["user-scopes"])


@router.get("/{user_id}/scopes", response_model=list[str])
async def get_user_scopes(
    user_id: str,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> list[str]:
    """Get all scopes assigned to a user. Superuser-bypassed."""
    repo = UserScopeRepository(session)
    scopes = await repo.get_scopes(user_id)
    return scopes


@router.put("/{user_id}/scopes", response_model=list[str])
async def set_user_scopes(
    user_id: str,
    scopes: list[str],
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> list[str]:
    """Replace all scopes assigned to a user."""
    repo = UserScopeRepository(session)
    await repo.set_scopes(user_id, scopes)
    return await repo.get_scopes(user_id)


@router.delete(
    "/{user_id}",
    status_code=204,
)
async def remove_all_user_scopes(
    user_id: str,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Remove all scopes from a user."""
    repo = UserScopeRepository(session)
    await repo.set_scopes(user_id, [])
