"""Repository for feature_flags table."""

from sqlmodel import func, select

from app.models import FeatureFlag


class FeatureFlagRepository:
    def __init__(self, session):
        self.session = session

    async def create(self, data: dict) -> FeatureFlag:
        flag = FeatureFlag.model_validate(data)
        self.session.add(flag)
        await self.session.commit()
        await self.session.refresh(flag)
        return flag  # type: ignore[no-any-return]

    async def get_by_id(self, id: str) -> FeatureFlag | None:
        statement = select(FeatureFlag).where(FeatureFlag.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_name(self, name: str) -> FeatureFlag | None:
        statement = select(FeatureFlag).where(FeatureFlag.name == name)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[FeatureFlag], int]:
        count_stmt = select(func.count(FeatureFlag.id))  # type: ignore[arg-type]
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        statement = select(FeatureFlag).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        items = list(result.scalars().all())
        return items, total

    async def update(self, db_item: FeatureFlag, data: dict) -> FeatureFlag:
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

    async def get_by_names(self, names: list[str]) -> list[FeatureFlag]:
        statement = select(FeatureFlag).where(
            FeatureFlag.name.in_(names)  # type: ignore[arg-type, attr-defined]
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_enabled_names(self) -> list[str]:
        statement = select(FeatureFlag).where(FeatureFlag.is_enabled == True)  # noqa: E712
        result = await self.session.execute(statement)
        return [f.name for f in result.scalars().all()]
