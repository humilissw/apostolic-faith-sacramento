from sqlmodel import func, select

from backend.models import FeatureFlag


class FeatureFlagRepository:
    def __init__(self, session):
        self.session = session

    def create(self, data: dict) -> FeatureFlag:
        flag = FeatureFlag.model_validate(data)
        self.session.add(flag)
        self.session.commit()
        self.session.refresh(flag)
        return flag

    def get_by_id(self, id: str) -> FeatureFlag | None:
        statement = select(FeatureFlag).where(FeatureFlag.id == id)
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def get_by_name(self, name: str) -> FeatureFlag | None:
        statement = select(FeatureFlag).where(FeatureFlag.name == name)
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[FeatureFlag], int]:
        count_stmt = select(func.count(FeatureFlag.id))
        count_result = self.session.execute(count_stmt)
        total = count_result.scalar() or 0
        statement = select(FeatureFlag).offset(skip).limit(limit)
        result = self.session.execute(statement)
        items = list(result.scalars().all())
        return items, total

    def update(self, db_item: FeatureFlag, data: dict) -> FeatureFlag:
        for key, value in data.items():
            if hasattr(db_item, key) and value is not None:
                setattr(db_item, key, value)
        db_item.updated_on = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def get_by_names(self, names: list[str]) -> list[FeatureFlag]:
        statement = select(FeatureFlag).where(FeatureFlag.name.in_(names))
        result = self.session.execute(statement)
        return list(result.scalars().all())

    def get_enabled_names(self) -> list[str]:
        statement = select(FeatureFlag).where(FeatureFlag.is_enabled.is_(True))
        result = self.session.execute(statement)
        return [f.name for f in result.scalars().all()]
