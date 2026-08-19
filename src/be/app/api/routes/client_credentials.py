"""Routes for managing OAuth2 client credentials."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    ClientCredentialsCreate,
    ClientCredentialsPublic,
    ClientCredentialsUpdate,
)
from app.services.client_credentials_service import ClientCredentialsService

router = APIRouter(prefix="/admin/client-credentials", tags=["client-credentials"])


@router.get("/", response_model=list[ClientCredentialsPublic])
async def list_client_credentials(
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> list[ClientCredentialsPublic]:
    """List all client credentials (superuser only)."""
    svc = ClientCredentialsService(session)
    return await svc.get_all()


@router.post("/", response_model=ClientCredentialsPublic, status_code=201)
async def create_client_credentials(
    body: ClientCredentialsCreate,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> ClientCredentialsPublic:
    """Create new client credentials (superuser only)."""
    svc = ClientCredentialsService(session)
    try:
        return await svc.create(client_id=body.client_id, scopes=body.scopes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.patch("/{cc_id}", response_model=ClientCredentialsPublic)
async def update_client_credentials(
    cc_id: str,
    body: ClientCredentialsUpdate,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> ClientCredentialsPublic:
    """Update client credentials (superuser only)."""
    svc = ClientCredentialsService(session)
    result = await svc.update(cc_id, scopes=body.scopes, is_active=body.is_active)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client credentials not found",
        )
    return ClientCredentialsService._to_public(result)


@router.delete("/{cc_id}", status_code=204)
async def delete_client_credentials(
    cc_id: str,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> None:
    """Delete client credentials (superuser only)."""
    svc = ClientCredentialsService(session)
    deleted = await svc.delete(cc_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client credentials not found",
        )
