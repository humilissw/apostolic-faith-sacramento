"""Routes for feature flag management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import FeatureFlagPublic, FeatureFlagsPublic
from app.repositories.feature_flag_repo import FeatureFlagRepository
from app.requests.feature_flag_request import FeatureFlagUpdateRequest
from app.services.feature_flag_service import (
    FeatureFlagService,
    KNOWN_FEATURE_FLAGS,
)

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


def _get_service(session) -> FeatureFlagService:
    return FeatureFlagService(FeatureFlagRepository(session))


@router.get("/", response_model=FeatureFlagsPublic)
async def list_feature_flags(
    session: SessionDep,
) -> FeatureFlagsPublic:
    """List all feature flags (public, no auth required)."""
    service = _get_service(session)
    items, total = await service.get_all()
    return FeatureFlagsPublic(
        data=[FeatureFlagPublic.model_validate(i.model_dump()) for i in items],
        count=total,
    )


@router.get("/names", response_model=list[str])
async def get_enabled_flag_names(
    session: SessionDep,
) -> list[str]:
    """Get names of all enabled feature flags."""
    service = _get_service(session)
    return await service.get_enabled_names()


@router.patch(
    "/{flag_name}",
    response_model=FeatureFlagPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_feature_flag(
    flag_name: str,
    update_in: FeatureFlagUpdateRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> FeatureFlagPublic:
    """Update a feature flag (superuser only)."""
    service = _get_service(session)
    flag = await service.get_by_name(flag_name)
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found",
        )

    update_data = update_in.model_dump(exclude_unset=True)
    updated = await service.update_enabled(flag, update_data.get("is_enabled", flag.is_enabled))
    return FeatureFlagPublic.model_validate(updated.model_dump())


@router.post(
    "/pre-seed",
    response_model=FeatureFlagsPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
async def pre_seed_feature_flags(
    session: SessionDep,
    current_user: CurrentUser,
) -> FeatureFlagsPublic:
    """Create default entries for all known feature flags (superuser only)."""
    service = _get_service(session)
    await service.pre_seed_flags()
    items, total = await service.get_all()
    return FeatureFlagsPublic(
        data=[FeatureFlagPublic.model_validate(i.model_dump()) for i in items],
        count=total,
    )


@router.get("/known", response_model=dict)
async def get_known_feature_flags() -> dict:
    """Get metadata for all known feature flags (public)."""
    return {
        name: {
            "display_name": meta["display_name"],
            "description": meta["description"],
            "icon": meta["icon"],
            "required_scopes": meta.get("required_scopes", []),
        }
        for name, meta in KNOWN_FEATURE_FLAGS.items()
    }
