from sqlalchemy import select

from backend.models import UserScope


class UserScopeRepository:
    def __init__(self, session) -> None:
        self.session = session

    def get_scopes(self, user_id: str) -> list[str]:
        statement = select(UserScope).where(UserScope.user_id == user_id)
        result = self.session.execute(statement)
        return [row[0].scope for row in result.all()]

    def set_scopes(self, user_id: str, scopes: list[str]) -> None:
        statement = select(UserScope).where(UserScope.user_id == user_id)
        result = self.session.execute(statement)
        for row in result.scalars().all():
            self.session.delete(row)
        self.session.commit()
        for scope in scopes:
            entry = UserScope(user_id=user_id, scope=scope)
            self.session.add(entry)
        self.session.commit()

    def has_scope(self, user_id: str, scope: str) -> bool:
        statement = select(UserScope).where(UserScope.user_id == user_id).where(UserScope.scope == scope)
        result = self.session.execute(statement)
        return result.first() is not None
