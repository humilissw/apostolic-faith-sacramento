from sqlalchemy import select, func

from backend.models import User, UserCreate, UserUpdate, UserUpdateMe
from backend.core.security import get_password_hash


class UserRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        session_user = self.session.execute(statement)
        return session_user.scalar_one_or_none()

    def get_by_id(self, user_id: int | str) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = self.session.execute(statement)
        user = result.scalar_one_or_none()
        if user:
            return user
        statement = select(User).where(User.new_id == str(user_id))
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        count_statement = select(func.count()).select_from(User)
        count_result = self.session.execute(count_statement)
        total_count = count_result.scalar()
        statement = select(User).offset(skip).limit(limit)
        result = self.session.execute(statement)
        users = result.scalars().all()
        return list(users), total_count or 0

    def update(self, db_user: User, user_in: UserUpdate | UserUpdateMe) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def delete(self, db_user: User) -> None:
        self.session.delete(db_user)
        self.session.commit()

    def update_password(self, db_user: User, new_password: str) -> User:
        hashed_password = get_password_hash(password=new_password)
        db_user.hashed_password = hashed_password
        self.session.add(db_user)
        self.session.flush()
        self.session.commit()
        return db_user
