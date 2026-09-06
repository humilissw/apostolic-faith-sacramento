"""Service for user management operations."""

from sqlalchemy import delete

from app.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserScope,
    UserUpdate,
    UserUpdateMe,
)
from app.repositories.user_repo import UserRepository
from app.repositories.user_scope_repo import UserScopeRepository
from app.services.auth_service import AuthService


class UserManagementService:
    """Handles business logic for user management operations."""

    def __init__(self, session):
        self.session = session

    async def create_user(self, user_create: UserCreate) -> UserPublic:
        """Create a new user and email them a link to set their own password.

        Administrators must never set a password on behalf of another user:
        any supplied password is rejected. The account is created with an
        unusable random password, and the user receives a new-account email
        containing an HMAC-signed, single-use link to choose their password.
        """
        if user_create.password is not None:
            raise ValueError(
                "Password cannot be set when creating a user. The user will "
                "receive an email with a one-time link to set their own password."
            )

        repository = UserRepository(session=self.session)
        existing_user = await repository.get_by_email(email=user_create.email)
        if existing_user:
            raise ValueError("The user with this email already exists in the system.")

        user = await repository.create(user_create=user_create)

        # Assign scopes if provided
        if user_create.scopes:
            scope_repo = UserScopeRepository(self.session)
            await scope_repo.set_scopes(user.id, user_create.scopes)

        # Send new-account email with a one-time set-password link.
        # The link is HMAC-signed and single-use (see AuthService /
        # core.reset_tokens); the plaintext password never leaves the server
        # because there is none.
        if settings.emails_enabled and user.email:
            try:
                auth_service = AuthService(user_repository=repository, session=self.session)
                await auth_service.send_set_password_email(user, reason="welcome")
            except Exception:
                import logging

                logging.getLogger(__name__).exception(
                    "Failed to send set-password email to new user %s", user.email
                )

        return await self._populate_scopes(user)

    async def update_user_me(self, current_user: User, user_in: UserUpdateMe) -> UserPublic:
        """Update the current user's profile."""
        repository = UserRepository(session=self.session)

        if user_in.email:
            existing_user = await repository.get_by_email(email=user_in.email)
            if existing_user and existing_user.new_id != current_user.new_id:
                raise ValueError("User with this email already exists")

        user_data = user_in.model_dump(exclude_unset=True)
        current_user.sqlmodel_update(user_data)
        self.session.add(current_user)
        await self.session.commit()
        await self.session.refresh(current_user)
        return UserPublic.model_validate(current_user)

    async def update_password_me(self, current_user: User, body: UpdatePassword) -> Message:
        """Update the current user's password."""
        if not verify_password(body.current_password, current_user.hashed_password):
            raise ValueError("Incorrect password")
        if body.current_password == body.new_password:
            raise ValueError("New password cannot be the same as the current one")

        hashed_password = get_password_hash(body.new_password)
        current_user.hashed_password = hashed_password
        self.session.add(current_user)
        await self.session.commit()
        return Message(message="Password updated successfully")

    async def delete_user_me(self, current_user: User) -> Message:
        """Delete the current user's account."""
        if current_user.is_superuser:
            raise ValueError("Super users are not allowed to delete themselves")

        user_id = str(current_user.id)
        scopes_stmt = delete(UserScope).where(  # type: ignore[arg-type]
            UserScope.user_id == user_id,  # type: ignore[arg-type]
        )
        await self.session.execute(scopes_stmt)
        await self.session.delete(current_user)
        await self.session.commit()
        return Message(message="User deleted successfully")

    async def bulk_delete_users(self, user_ids: list[str]) -> Message:
        """Delete multiple users and their associated data."""
        if not user_ids:
            return Message(message="No user IDs provided")

        deleted = 0
        skipped = 0

        for uid in user_ids:
            repository = UserRepository(self.session)
            user = await repository.get_by_id(uid)
            if user:
                user_id_str = str(user.id)
                items_stmt = delete(Item).where(Item.owner_id == user.id)  # type: ignore[arg-type]
                await self.session.execute(items_stmt)
                scopes_stmt = delete(UserScope).where(
                    UserScope.user_id == user_id_str  # type: ignore[arg-type]
                )
                await self.session.execute(scopes_stmt)
                await self.session.delete(user)
                deleted += 1
            else:
                skipped += 1

        await self.session.commit()
        detail = f"Deleted {deleted} users"
        if skipped > 0:
            detail += f", {skipped} not found (skipped)"
        return Message(message=detail)

    async def delete_user(self, user_id: str, current_user: User) -> Message:
        """Delete a specific user."""
        repository = UserRepository(session=self.session)
        user = await repository.get_by_id(user_id=user_id)
        if not user:
            raise ValueError("User not found")
        if user == current_user:
            raise ValueError("Super users are not allowed to delete themselves")

        user_id_str = str(user.id)
        items_stmt = delete(Item).where(Item.owner_id == user_id)  # type: ignore[arg-type]
        await self.session.execute(items_stmt)  # type: ignore
        scopes_stmt = delete(UserScope).where(
            UserScope.user_id == user_id_str  # type: ignore[arg-type]
        )
        await self.session.execute(scopes_stmt)
        await self.session.delete(user)
        await self.session.commit()
        return Message(message="User deleted successfully")

    async def update_user(self, user_id: str, user_in: UserUpdate) -> UserPublic:
        """Update a specific user."""
        repository = UserRepository(session=self.session)
        db_user = await repository.get_by_id(user_id=user_id)
        if not db_user:
            raise ValueError("The user with this id does not exist in the system")

        if user_in.email:
            existing_user = await repository.get_by_email(email=user_in.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("User with this email already exists")

        db_user = await repository.update(db_user=db_user, user_in=user_in)
        return await self._populate_scopes(db_user)

    async def _populate_scopes(self, user: User) -> UserPublic:
        """Return a UserPublic with assigned_scopes populated."""
        repo = UserScopeRepository(self.session)
        scopes = await repo.get_scopes(user.id)
        return UserPublic(
            email=user.email,
            is_active=user.is_active,
            id=user.id,
            new_id=user.new_id,
            full_name=user.full_name,
            assigned_scopes=scopes,
        )
