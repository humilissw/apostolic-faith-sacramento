"""Routes for managing OAuth2 client credentials."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    ClientCredentials,
    ClientCredentialsCreate,
    ClientCredentialsPublic,
    ClientCredentialsUpdate,
)
from sqlalchemy import select

router = APIRouter(prefix="/admin/client-credentials", tags=["client-credentials"])


def _to_public(cc: ClientCredentials) -> ClientCredentialsPublic:
    return ClientCredentialsPublic(
        id=cc.id,
        client_id=cc.client_id,
        scopes=cc.scopes.split(",") if cc.scopes else [],
        is_active=cc.is_active,
    )


@router.get("/", response_model=list[ClientCredentialsPublic])
async def list_client_credentials(
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> list[ClientCredentialsPublic]:
    """List all client credentials (superuser only)."""
    result = await session.execute(select(ClientCredentials))
    return [
        ClientCredentialsPublic(
            id=cc.id,
            client_id=cc.client_id,
            scopes=cc.scopes.split(",") if cc.scopes else [],
            is_active=cc.is_active,
        )
        for cc in result.scalars().all()
    ]


@router.post("/", response_model=ClientCredentialsPublic, status_code=201)
async def create_client_credentials(
    body: ClientCredentialsCreate,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> ClientCredentialsPublic:
    """Create new client credentials (superuser only)."""
    result = await session.execute(
        select(ClientCredentials).where(
            ClientCredentials.client_id == body.client_id  # type: ignore[arg-type]
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client ID already exists",
        )

    import secrets

    client_secret = secrets.token_urlsafe(32)
    from app.core.security import get_password_hash

    hashed = get_password_hash(client_secret)

    db_cc = ClientCredentials(
        client_id=body.client_id,
        client_secret_hash=hashed,
        scopes=",".join(body.scopes),
    )
    session.add(db_cc)
    await session.commit()
    await session.refresh(db_cc)

    return ClientCredentialsPublic(
        id=db_cc.id,
        client_id=db_cc.client_id,
        scopes=db_cc.scopes.split(",") if db_cc.scopes else [],
        is_active=db_cc.is_active,
    )


@router.patch("/{cc_id}", response_model=ClientCredentialsPublic)
async def update_client_credentials(
    cc_id: str,
    body: ClientCredentialsUpdate,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> ClientCredentialsPublic:
    """Update client credentials (superuser only)."""
    result = await session.execute(
        select(ClientCredentials).where(ClientCredentials.id == cc_id)  # type: ignore[arg-type]
    )
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client credentials not found",
        )

    if body.scopes is not None:
        cc.scopes = ",".join(body.scopes)
    if body.is_active is not None:
        cc.is_active = body.is_active

    await session.commit()
    await session.refresh(cc)

    return ClientCredentialsPublic(
        id=cc.id,
        client_id=cc.client_id,
        scopes=cc.scopes.split(",") if cc.scopes else [],
        is_active=cc.is_active,
    )


@router.delete("/{cc_id}", status_code=204)
async def delete_client_credentials(
    cc_id: str,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> None:
    """Delete client credentials (superuser only)."""
    result = await session.execute(
        select(ClientCredentials).where(ClientCredentials.id == cc_id)  # type: ignore[arg-type]
    )
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client credentials not found",
        )
    await session.delete(cc)
    await session.commit()
