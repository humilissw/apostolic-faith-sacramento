"""Repository for integration_configs table."""

from sqlmodel import func, select

from app.models import IntegrationConfig


class IntegrationConfigRepository:
    def __init__(self, session):
        self.session = session

    async def create(self, data: dict) -> IntegrationConfig:
        config = IntegrationConfig.model_validate(data)
        self.session.add(config)
        await self.session.commit()
        await self.session.refresh(config)
        return config  # type: ignore[no-any-return]

    async def get_by_id(self, id: str) -> IntegrationConfig | None:
        statement = select(IntegrationConfig).where(IntegrationConfig.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_type(self, type: str) -> IntegrationConfig | None:
        statement = select(IntegrationConfig).where(IntegrationConfig.type == type)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[IntegrationConfig], int]:
        count_stmt = select(func.count(IntegrationConfig.id))  # type: ignore[arg-type]
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        statement = select(IntegrationConfig).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        items = list(result.scalars().all())
        return items, total

    async def update(self, db_item: IntegrationConfig, data: dict) -> IntegrationConfig:
        for key, value in data.items():
            if hasattr(db_item, key) and value is not None:
                setattr(db_item, key, value)
        db_item.updated_on = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        )
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def delete(self, db_item: IntegrationConfig) -> None:
        await self.session.delete(db_item)
        await self.session.commit()

    async def get_enabled(self) -> list[IntegrationConfig]:
        statement = select(IntegrationConfig).where(IntegrationConfig.enabled == True)  # noqa: E712
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_all_with_credentials(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[IntegrationConfig], int]:
        return await self.get_all(skip, limit)

    @staticmethod
    def _count_expr():
        from sqlalchemy import func

        return select(func.count()).select_from(IntegrationConfig)
