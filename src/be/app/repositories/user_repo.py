from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserCreate, UserUpdate, UserUpdateMe
from app.core.security import get_password_hash


class UserRepository:
    """
    Repository for User entity operations.
    Handles all database interactions for user entries.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, user_create: UserCreate) -> User:
        """
        Create a new user entry.

        Args:
            user_create: UserCreate object containing user data

        Returns:
            User: Created user object
        """
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj  # type: ignore[no-any-return]

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user entry by email.

        Args:
            email: Email address of the user

        Returns:
            User | None: User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)  # type: ignore[arg-type]
        session_user = await self.session.execute(statement)
        return session_user.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_id(self, user_id: int | str) -> User | None:
        """
        Retrieve a user entry by id or new_id.
        """
        statement = select(User).where(User.id == user_id)  # type: ignore[arg-type]
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()
        if user:
            return user  # type: ignore[no-any-return]
        statement = select(User).where(User.new_id == str(user_id))  # type: ignore[arg-type]
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """
        Retrieve all user entries with pagination.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)

        Returns:
            tuple[list[User], int]: Tuple of (users list, total count)
        """
        # Get total count
        count_statement = select(func.count()).select_from(User)
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar()

        # Get paginated results
        statement = select(User).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        users = result.scalars().all()

        return list(users), total_count or 0

    async def update(self, db_user: User, user_in: UserUpdate | UserUpdateMe) -> User:
        """
        Update an existing user entry.

        Args:
            db_user: User object to update
            user_in: UserUpdate or UserUpdateMe object with update data

        Returns:
            User: Updated user object
        """
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def delete(self, db_user: User) -> None:
        """
        Delete a user entry.

        Args:
            db_user: User object to delete
        """
        await self.session.delete(db_user)
        await self.session.commit()

    async def update_password(self, db_user: User, new_password: str) -> User:
        """
        Update a user's password.

        Args:
            db_user: User object to update
            new_password: New password to set

        Returns:
            User: Updated user object
        """
        # Hash the new password
        hashed_password = get_password_hash(password=new_password)
        # Update the password hash
        db_user.hashed_password = hashed_password
        # Add and flush the changes
        self.session.add(db_user)
        await self.session.flush()
        # Commit the changes to make them permanent
        await self.session.commit()
        return db_user
