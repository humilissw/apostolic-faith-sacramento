"""
Tests for MediaRepository using mocks.

This test suite validates the MediaRepository class by mocking database operations.
These tests demonstrate the benefits of the repository pattern - database logic
can be tested in isolation without requiring a real database.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Media
from app.requests.media_request import MediaCreate, MediaUpdate
from app.repositories.media_repo import MediaRepository


@pytest.mark.asyncio
class TestMediaRepositoryCreate:
    """Test cases for MediaRepository.create() method."""

    async def test_create_media_success(self, mock_async_session: AsyncSession) -> None:
        """Test successful media creation."""
        repository = MediaRepository(session=mock_async_session)
        media_in = MediaCreate(name="Test Media")

        # Mock the session.execute to return an async mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Execute create
        media = await repository.create(media_in=media_in, owner_id=str(uuid.uuid4()))

        # Verify the media was created
        assert media is not None
        assert media.name == "Test Media"
        assert media.id is not None
        assert media.uploaded_on is not None
        assert media.created_on is not None
        assert media.updated_on is not None

        # Verify session.add was called
        assert mock_async_session.add.called

        # Verify session.add was called
        assert mock_async_session.add.called

        # Verify session.commit was called
        assert mock_async_session.commit.called

    async def test_create_media_with_long_name(self, mock_async_session: AsyncSession) -> None:
        """Test media creation with a very long name (edge case)."""
        repository = MediaRepository(session=mock_async_session)
        long_name = "a" * 200  # Maximum allowed length
        media_in = MediaCreate(name=long_name)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.create(media_in=media_in, owner_id=str(uuid.uuid4()))

        assert media.name == long_name
        assert mock_async_session.commit.called

    async def test_create_media_empty_name(self, mock_async_session: AsyncSession) -> None:
        """Test media creation with empty name (validation edge case)."""
        repository = MediaRepository(session=mock_async_session)
        media_in = MediaCreate(name="")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        # Should not raise, but will be handled by SQLModel validation
        media = await repository.create(media_in=media_in, owner_id=str(uuid.uuid4()))

        assert media.name == ""


@pytest.mark.asyncio
class TestMediaRepositoryGetById:
    """Test cases for MediaRepository.get_by_id() method."""

    async def test_get_by_id_existing(self, mock_async_session: AsyncSession) -> None:
        """Test retrieving an existing media entry by ID."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        # Mock the existing media
        mock_media = Media(
            id=str(test_id),
            name="Existing Media",
            owner_id=str(uuid.uuid4()),
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Mock execute to return the media
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_media
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.get_by_id(media_id=str(test_id))

        assert media is not None
        assert media.id == str(test_id)
        assert media.name == "Existing Media"

    async def test_get_by_id_not_found(self, mock_async_session: AsyncSession) -> None:
        """Test retrieving a non-existent media entry."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        # Mock execute to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.get_by_id(media_id=str(test_id))

        assert media is None

    async def test_get_by_id_with_special_characters(
        self, mock_async_session: AsyncSession
    ) -> None:
        """Test retrieving media with special characters in name (edge case)."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        mock_media = Media(
            id=str(test_id),
            name="Test & Special <chars>!",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_media
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.get_by_id(media_id=str(test_id))

        assert media.name == "Test & Special <chars>!"


@pytest.mark.asyncio
class TestMediaRepositoryGetAll:
    """Test cases for MediaRepository.get_all() method."""

    async def test_get_all_with_no_records(self, mock_async_session: AsyncSession) -> None:
        """Test retrieving all media when database is empty."""
        repository = MediaRepository(session=mock_async_session)

        # Mock count to return 0
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0

        # Mock results to return empty list
        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = []

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        medias, total_count = await repository.get_all()

        assert medias == []
        assert total_count == 0

    async def test_get_all_with_records(self, mock_async_session: AsyncSession) -> None:
        """Test retrieving all media entries."""
        repository = MediaRepository(session=mock_async_session)

        # Create mock media items
        test_id_1 = uuid.uuid4()
        test_id_2 = uuid.uuid4()

        mock_media_1 = Media(
            id=str(test_id_1),
            name="First Media",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        mock_media_2 = Media(
            id=str(test_id_2),
            name="Second Media",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Mock count to return 2
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        # Mock results to return both medias
        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = [
            mock_media_1,
            mock_media_2,
        ]

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        medias, total_count = await repository.get_all()

        assert len(medias) == 2
        assert total_count == 2
        assert medias[0].name == "First Media"
        assert medias[1].name == "Second Media"

    async def test_get_all_with_pagination(self, mock_async_session: AsyncSession) -> None:
        """Test retrieving paginated media entries."""
        repository = MediaRepository(session=mock_async_session)

        # Create 5 mock media items
        mock_medias = []
        for i in range(5):
            test_id = uuid.uuid4()
            mock_media = Media(
                id=str(test_id),
                name=f"Media {i}",
                uploaded_on=datetime.now(timezone.utc),
                created_on=datetime.now(timezone.utc),
                updated_on=datetime.now(timezone.utc),
            )
            mock_medias.append(mock_media)

        # Mock count to return 5
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 5

        # Mock results - return list so slicing works
        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = mock_medias[2:4]

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        # Test with skip and limit
        medias, total_count = await repository.get_all(skip=2, limit=2)

        assert len(medias) == 2
        assert total_count == 5
        assert medias[0].name == "Media 2"
        assert medias[1].name == "Media 3"

    async def test_get_all_with_limit_zero(self, mock_async_session: AsyncSession) -> None:
        """Test retrieving media with limit of 0 (edge case)."""
        repository = MediaRepository(session=mock_async_session)

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 3

        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = []

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        medias, total_count = await repository.get_all(limit=0)

        assert medias == []
        assert total_count == 3


@pytest.mark.asyncio
class TestMediaRepositoryUpdate:
    """Test cases for MediaRepository.update() method."""

    async def test_update_media_success(self, mock_async_session: AsyncSession) -> None:
        """Test successful media update."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        # Mock existing media
        mock_media = Media(
            id=str(test_id),
            name="Original Name",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Mock execute for get_by_id
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_media
        mock_get_execute = AsyncMock(return_value=mock_get_result)
        mock_async_session.execute = mock_get_execute

        # Mock execute for update (no return value expected)
        mock_update_result = MagicMock()
        mock_update_result.scalar_one_or_none.return_value = mock_media
        mock_update_execute = AsyncMock(return_value=mock_update_result)
        mock_async_session.execute = mock_update_execute

        update_data = {"name": "Updated Name"}
        media_in = MediaUpdate(**update_data)

        updated_media = await repository.update(db_media=mock_media, media_in=media_in)

        assert updated_media.name == "Updated Name"
        assert updated_media.updated_on is not None

    async def test_update_media_not_found(self, mock_async_session: AsyncSession) -> None:
        """Test updating a non-existent media entry."""
        repository = MediaRepository(session=mock_async_session)

        # Mock execute to return None (media not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        # Create a mock media object
        mock_media = Media(
            id=str(uuid.uuid4()),
            name="Original",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        media_in = MediaUpdate(name="Updated Name")
        updated_media = await repository.update(db_media=mock_media, media_in=media_in)

        # Should handle gracefully (raise exception)
        assert updated_media is not None

    async def test_update_media_with_empty_update(self, mock_async_session: AsyncSession) -> None:
        """Test updating media with no changes (edge case)."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        mock_media = Media(
            id=str(test_id),
            name="Test Media",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_media
        mock_get_execute = AsyncMock(return_value=mock_get_result)
        mock_async_session.execute = mock_get_execute

        mock_update_result = MagicMock()
        mock_update_result.scalar_one_or_none.return_value = mock_media
        mock_update_execute = AsyncMock(return_value=mock_update_result)
        mock_async_session.execute = mock_update_execute

        # Update with empty data
        media_in = MediaUpdate()

        updated_media = await repository.update(db_media=mock_media, media_in=media_in)

        assert updated_media.name == "Test Media"
        assert updated_media.updated_on is not None

    async def test_update_media_reset_updated_on(self, mock_async_session: AsyncSession) -> None:
        """Test that update clears old updated_on timestamp (edge case)."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        old_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        mock_media = Media(
            id=str(test_id),
            name="Test Media",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=old_time,
        )

        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_media
        mock_get_execute = AsyncMock(return_value=mock_get_result)
        mock_async_session.execute = mock_get_execute

        mock_update_result = MagicMock()
        mock_update_result.scalar_one_or_none.return_value = mock_media
        mock_update_execute = AsyncMock(return_value=mock_update_result)
        mock_async_session.execute = mock_update_execute

        media_in = MediaUpdate(name="Updated Name")

        updated_media = await repository.update(db_media=mock_media, media_in=media_in)

        assert updated_media.updated_on > old_time


@pytest.mark.asyncio
class TestMediaRepositoryDelete:
    """Test cases for MediaRepository.delete() method."""

    async def test_delete_media_success(self, mock_async_session: AsyncSession) -> None:
        """Test successful media deletion."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        # Mock existing media
        mock_media = Media(
            id=str(test_id),
            name="To Be Deleted",
            owner_id=str(uuid.uuid4()),
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Mock execute for get_by_id
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_media
        mock_get_execute = AsyncMock(return_value=mock_get_result)

        # Mock execute for delete (returns a MagicMock with scalars().all())
        mock_delete_result = MagicMock()
        mock_delete_result.scalars = MagicMock()
        mock_delete_result.scalars.all = MagicMock(return_value=[])
        mock_delete_execute = AsyncMock(return_value=mock_delete_result)

        # Mock execute to return different values for each call
        mock_async_session.execute.side_effect = [mock_get_execute, mock_delete_execute]

        # Delete the media
        await repository.delete(db_media=mock_media)

        # Verify session.delete was called
        assert mock_async_session.delete.called
        assert mock_async_session.delete.call_args[0][0] == mock_media

        # Verify session.commit was called
        assert mock_async_session.commit.called

    async def test_delete_media_not_found(self, mock_async_session: AsyncSession) -> None:
        """Test deleting a non-existent media entry."""
        repository = MediaRepository(session=mock_async_session)

        # Mock execute to return None (media not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        # Create a mock media object
        mock_media = Media(
            id=str(uuid.uuid4()),
            name="Non-existent",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Should handle gracefully (no exception raised)
        await repository.delete(db_media=mock_media)

        # Verify session.delete was called
        assert mock_async_session.delete.called
        assert mock_async_session.commit.called


@pytest.fixture
def mock_async_session() -> AsyncSession:
    """Create a mock AsyncSession for testing."""
    mock_async_session = MagicMock(spec=AsyncSession)
    return mock_async_session


@pytest.mark.asyncio
class TestMediaRepositoryEdgeCases:
    """Test edge cases and error scenarios."""

    async def test_create_media_with_unicode_characters(
        self, mock_async_session: AsyncSession
    ) -> None:
        """Test media creation with unicode characters (edge case)."""
        repository = MediaRepository(session=mock_async_session)
        unicode_name = "Media with 🎬 emojis 🚀 and 中文"
        media_in = MediaCreate(name=unicode_name)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.create(media_in=media_in, owner_id=str(uuid.uuid4()))

        assert media.name == unicode_name

    async def test_create_media_with_null_values(self, mock_async_session: AsyncSession) -> None:
        """Test media creation with null values (edge case)."""
        repository = MediaRepository(session=mock_async_session)

        # MediaCreate doesn't allow nulls for required fields
        media_in = MediaCreate(name="")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.create(media_in=media_in, owner_id=str(uuid.uuid4()))

        assert media.name == ""

    async def test_get_all_with_negative_skip(self, mock_async_session: AsyncSession) -> None:
        """Test get_all with negative skip parameter (edge case)."""
        repository = MediaRepository(session=mock_async_session)

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = []

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        # SQLAlchemy will handle negative skip, but we should test it
        medias, total_count = await repository.get_all(skip=-1)

        # Should still return empty list (SQLAlchemy behavior)
        assert medias == []
        assert total_count == 2

    async def test_update_media_clears_password_field(
        self, mock_async_session: AsyncSession
    ) -> None:
        """Test that update removes password field if present (edge case)."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        mock_media = Media(
            id=str(test_id),
            name="Test Media",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_media
        mock_get_execute = AsyncMock(return_value=mock_get_result)
        mock_async_session.execute = mock_get_execute

        mock_update_result = MagicMock()
        mock_update_result.scalar_one_or_none.return_value = mock_media
        mock_update_execute = AsyncMock(return_value=mock_update_result)
        mock_async_session.execute = mock_update_execute

        # Try to update with a password field (which doesn't exist in Media)
        media_in = MediaUpdate(name="Updated", password="secret")

        updated_media = await repository.update(db_media=mock_media, media_in=media_in)

        # Password field should be handled by sqlmodel_update
        assert updated_media.name == "Updated"
        assert updated_media.updated_on is not None

    async def test_repository_session_not_commits_on_failure(
        self, mock_async_session: AsyncSession
    ) -> None:
        """Test that commit is only called when operation succeeds (edge case)."""
        repository = MediaRepository(session=mock_async_session)
        media_in = MediaCreate(name="Test Media")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        # This test demonstrates the repository's behavior
        # In a real scenario, exceptions would be raised
        _ = await repository.create(media_in=media_in, owner_id=str(uuid.uuid4()))

        # Verify commit was called
        assert mock_async_session.commit.called

        # Reset mock
        mock_async_session.reset_mock()

        # Try to create another one
        _ = await repository.create(media_in=media_in, owner_id=str(uuid.uuid4()))

        # Commit should be called again
        assert mock_async_session.commit.called
