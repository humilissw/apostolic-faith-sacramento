"""Service for OAuth2 client credentials management."""

import secrets

from app.core.security import get_password_hash
from app.models import ClientCredentials, ClientCredentialsPublic


class ClientCredentialsService:
    """Handles business logic for client credentials CRUD operations."""

    def __init__(self, session):
        self.session = session

    @staticmethod
    def _to_public(cc: ClientCredentials) -> ClientCredentialsPublic:
        """Convert a ClientCredentials model to its public representation."""
        return ClientCredentialsPublic(
            id=cc.id,
            client_id=cc.client_id,
            scopes=cc.scopes.split(",") if cc.scopes else [],
            is_active=cc.is_active,
        )

    async def get_all(self) -> list[ClientCredentialsPublic]:
        """Get all client credentials as public representations."""
        from sqlalchemy import select

        result = await self.session.execute(select(ClientCredentials))
        return [self._to_public(cc) for cc in result.scalars().all()]

    async def create(self, client_id: str, scopes: list[str]) -> ClientCredentialsPublic:
        """Create new client credentials with hashed secret.

        Returns the public representation. Raises ValueError if client_id already exists.
        """
        from sqlalchemy import select

        result = await self.session.execute(
            select(ClientCredentials).where(  # type: ignore[arg-type]
                ClientCredentials.client_id == client_id,  # type: ignore[arg-type]
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Client ID already exists")

        client_secret = secrets.token_urlsafe(32)
        hashed = get_password_hash(client_secret)

        db_cc = ClientCredentials(
            client_id=client_id,
            client_secret_hash=hashed,
            scopes=",".join(scopes),
        )
        self.session.add(db_cc)
        await self.session.commit()
        await self.session.refresh(db_cc)

        return self._to_public(db_cc)

    async def update(
        self, cc_id: str, scopes: list[str] | None = None, is_active: bool | None = None
    ):
        """Update client credentials. Returns updated model or None if not found."""
        from sqlalchemy import select

        result = await self.session.execute(
            select(ClientCredentials).where(ClientCredentials.id == cc_id)  # type: ignore[arg-type]
        )
        cc = result.scalar_one_or_none()
        if not cc:
            return None

        if scopes is not None:
            cc.scopes = ",".join(scopes)
        if is_active is not None:
            cc.is_active = is_active

        await self.session.commit()
        await self.session.refresh(cc)
        return cc

    async def delete(self, cc_id: str) -> bool:
        """Delete client credentials. Returns True if deleted, False if not found."""
        from sqlalchemy import select

        result = await self.session.execute(
            select(ClientCredentials).where(ClientCredentials.id == cc_id)  # type: ignore[arg-type]
        )
        cc = result.scalar_one_or_none()
        if not cc:
            return False
        await self.session.delete(cc)
        await self.session.commit()
        return True
