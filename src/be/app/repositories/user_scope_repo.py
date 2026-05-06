"""Repository for user-scoped permissions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserScope


class UserScopeRepository:
    """Repository for UserScope entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_scopes(self, user_id: str) -> list[str]:
        statement = select(UserScope).where(UserScope.user_id == user_id)  # type: ignore[arg-type]
        result = await self.session.execute(statement)
        return [row[0].scope for row in result.all()]  # type: ignore[no-any-return]

    async def set_scopes(self, user_id: str, scopes: list[str]) -> None:
        # Remove existing scopes
        statement = select(UserScope).where(UserScope.user_id == user_id)  # type: ignore[arg-type]
        result = await self.session.execute(statement)
        for row in result.scalars().all():
            await self.session.delete(row)  # type: ignore[arg-type]
        await self.session.commit()
        # Add new scopes
        for scope in scopes:
            entry = UserScope(user_id=user_id, scope=scope)
            self.session.add(entry)
        await self.session.commit()

    async def has_scope(self, user_id: str, scope: str) -> bool:
        statement = (
            select(UserScope)
            .where(UserScope.user_id == user_id)  # type: ignore[arg-type]
            .where(UserScope.scope == scope)  # type: ignore[arg-type]
        )
        result = await self.session.execute(statement)
        return result.first() is not None
