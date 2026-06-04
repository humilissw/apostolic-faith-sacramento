"""Tests for RefreshToken and User model type compatibility."""

import uuid

from app.models import RefreshToken, User


class TestRefreshTokenModel:
    """Ensure RefreshToken uses str user_id matching User.id."""

    def test_user_id_is_str(self) -> None:
        """RefreshToken.user_id must be a str (UUID) to match User.id."""
        user_id = str(uuid.uuid4())
        token = RefreshToken(
            user_id=user_id,
            token="test-token-value",
        )
        assert token.user_id == user_id
        assert isinstance(token.user_id, str)

    def test_refresh_token_accepts_uuid_string(self) -> None:
        """A RefreshToken created with a UUID string must serialize correctly."""
        user_id = str(uuid.uuid4())
        token = RefreshToken(
            user_id=user_id,
            token="opaque-refresh-token",
        )
        dict_repr = token.model_dump()
        assert dict_repr["user_id"] == user_id
        assert isinstance(dict_repr["user_id"], str)


class TestUserNewId:
    """Ensure User model has new_id field for API compatibility."""

    def test_user_has_new_id_field(self) -> None:
        """User must have a new_id str field."""
        user = User(
            email="test@example.com",
            hashed_password="hashed",
        )
        assert user.new_id is not None
        assert isinstance(user.new_id, str)

    def test_user_new_id_is_valid_uuid(self) -> None:
        """new_id must be a valid UUID string."""
        user = User(
            email="test@example.com",
            hashed_password="hashed",
        )
        # Should not raise — validates it's a proper UUID
        parsed = uuid.UUID(user.new_id)
        assert str(parsed) == user.new_id
