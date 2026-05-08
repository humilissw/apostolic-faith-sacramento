"""
Standalone tests for MediaRepository using mocks.

These tests demonstrate how to test repository methods with mock objects
without requiring environment configuration or database connections.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Media
from app.requests.media_request import MediaCreate, MediaUpdate
from app.repositories.media_repo import MediaRepository


@pytest.fixture
def mock_async_session() -> AsyncSession:
    """Create a mock AsyncSession for testing repositories."""
    mock_session = MagicMock(spec=AsyncSession)
    return mock_session


@pytest.mark.asyncio
class TestMediaRepositoryBasicOperations:
    """Basic CRUD operation tests for MediaRepository."""

    async def test_repository_initialization(self, mock_async_session: AsyncSession) -> None:
        """Test repository initialization with session."""
        repository = MediaRepository(session=mock_async_session)

        assert repository.session == mock_async_session

    async def test_create_media(self, mock_async_session: AsyncSession) -> None:
        """Test creating a new media entry."""
        repository = MediaRepository(session=mock_async_session)
        media_in = MediaCreate(name="Test Media")

        # Mock the result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.create(media_in=media_in)

        assert media is not None
        assert media.name == "Test Media"
        assert mock_async_session.add.called

    async def test_get_by_id(self, mock_async_session: AsyncSession) -> None:
        """Test getting media by ID."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        # Mock existing media
        mock_media = Media(
            id=str(test_id),
            name="Found Media",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_media
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.get_by_id(media_id=str(test_id))

        assert media is not None
        assert media.id == str(test_id)
        assert media.name == "Found Media"

    async def test_get_by_id_not_found(self, mock_async_session: AsyncSession) -> None:
        """Test getting media by ID when it doesn't exist."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.get_by_id(media_id=str(test_id))

        assert media is None

    async def test_update_media(self, mock_async_session: AsyncSession) -> None:
        """Test updating an existing media entry."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        # Mock existing media
        mock_media = Media(
            id=str(test_id),
            name="Original",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Mock get_by_id
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_media
        mock_get_execute = AsyncMock(return_value=mock_get_result)
        mock_async_session.execute = mock_get_execute

        # Mock update
        mock_update_result = MagicMock()
        mock_update_result.scalar_one_or_none.return_value = mock_media
        mock_update_execute = AsyncMock(return_value=mock_update_result)
        mock_async_session.execute = mock_update_execute

        update_data = {"name": "Updated"}
        media_in = MediaUpdate(**update_data)

        updated_media = await repository.update(db_media=mock_media, media_in=media_in)

        assert updated_media.name == "Updated"
        assert updated_media.updated_on is not None

    async def test_delete_media(self, mock_async_session: AsyncSession) -> None:
        """Test deleting a media entry."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        # Mock existing media
        mock_media = Media(
            id=str(test_id),
            name="To Delete",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Mock get_by_id
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_media
        mock_get_execute = AsyncMock(return_value=mock_get_result)
        mock_async_session.execute = mock_get_execute

        # Mock delete
        mock_delete_result = MagicMock()
        mock_delete_execute = AsyncMock(return_value=mock_delete_result)
        mock_async_session.execute = mock_delete_execute

        await repository.delete(db_media=mock_media)

        assert mock_async_session.delete.called
        assert mock_async_session.delete.call_args[0][0] == mock_media
        assert mock_async_session.commit.called


@pytest.mark.asyncio
class TestMediaRepositoryPagination:
    """Test pagination functionality of MediaRepository."""

    async def test_get_all_empty(self, mock_async_session: AsyncSession) -> None:
        """Test getting all media when database is empty."""
        repository = MediaRepository(session=mock_async_session)

        # Mock count
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0

        # Mock results
        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = []

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        medias, total_count = await repository.get_all()

        assert medias == []
        assert total_count == 0

    async def test_get_all_with_data(self, mock_async_session: AsyncSession) -> None:
        """Test getting all media entries."""
        repository = MediaRepository(session=mock_async_session)

        # Create mock medias
        mock_medias = []
        for i in range(3):
            mock_media = Media(
                id=str(uuid.uuid4()),
                name=f"Media {i}",
                uploaded_on=datetime.now(timezone.utc),
                created_on=datetime.now(timezone.utc),
                updated_on=datetime.now(timezone.utc),
            )
            mock_medias.append(mock_media)

        # Mock count
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 3

        # Mock results
        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = mock_medias

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        medias, total_count = await repository.get_all()

        assert len(medias) == 3
        assert total_count == 3
        assert medias[0].name == "Media 0"
        assert medias[1].name == "Media 1"
        assert medias[2].name == "Media 2"


@pytest.mark.asyncio
class TestMediaRepositoryEdgeCases:
    """Test edge cases and error scenarios."""

    async def test_create_with_very_long_name(self, mock_async_session: AsyncSession) -> None:
        """Test creating media with very long name (200 chars)."""
        repository = MediaRepository(session=mock_async_session)
        long_name = "a" * 200
        media_in = MediaCreate(name=long_name)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.create(media_in=media_in)

        assert media.name == long_name

    async def test_create_with_emoji_name(self, mock_async_session: AsyncSession) -> None:
        """Test creating media with emoji in name."""
        repository = MediaRepository(session=mock_async_session)
        emoji_name = "🎬 Movie 🎬"
        media_in = MediaCreate(name=emoji_name)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.create(media_in=media_in)

        assert media.name == emoji_name

    async def test_create_with_unicode_name(self, mock_async_session: AsyncSession) -> None:
        """Test creating media with unicode characters."""
        repository = MediaRepository(session=mock_async_session)
        unicode_name = "Café naïve résumé"
        media_in = MediaCreate(name=unicode_name)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_execute = AsyncMock(return_value=mock_result)
        mock_async_session.execute = mock_execute

        media = await repository.create(media_in=media_in)

        assert media.name == unicode_name

    async def test_update_with_empty_fields(self, mock_async_session: AsyncSession) -> None:
        """Test updating media with empty update data."""
        repository = MediaRepository(session=mock_async_session)
        test_id = uuid.uuid4()

        mock_media = Media(
            id=str(test_id),
            name="Test",
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

        media_in = MediaUpdate()

        updated_media = await repository.update(db_media=mock_media, media_in=media_in)

        assert updated_media.name == "Test"
        assert updated_media.updated_on is not None

    async def test_delete_non_existent(self, mock_async_session: AsyncSession) -> None:
        """Test deleting media that doesn't exist."""
        repository = MediaRepository(session=mock_async_session)

        mock_media = Media(
            id=str(uuid.uuid4()),
            name="Non-existent",
            uploaded_on=datetime.now(timezone.utc),
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )

        # Delete should still be called even if media doesn't exist
        # The repository doesn't check if media exists before deleting
        await repository.delete(db_media=mock_media)

        # Verify delete was called (no exception raised)
        assert mock_async_session.delete.called
        assert mock_async_session.commit.called

    async def test_get_all_with_limit_zero(self, mock_async_session: AsyncSession) -> None:
        """Test get_all with limit of 0."""
        repository = MediaRepository(session=mock_async_session)

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        mock_results = MagicMock()
        mock_results.scalars.return_value.all.return_value = []

        mock_execute = AsyncMock()
        mock_execute.side_effect = [mock_count_result, mock_results]
        mock_async_session.execute = mock_execute

        medias, total_count = await repository.get_all(limit=0)

        assert medias == []
        assert total_count == 2


@pytest.mark.asyncio
class TestMediaRepositoryIntegrationScenarios:
    """Test realistic integration scenarios."""

    async def test_full_crud_workflow(self, mock_async_session: AsyncSession) -> None:
        """Test a complete CRUD workflow."""
        repository = MediaRepository(session=mock_async_session)

        # 1. Create
        create_media_in = MediaCreate(name="First Media")
        mock_create_result = MagicMock()
        mock_create_result.scalar_one_or_none.return_value = None
        mock_async_session.execute = AsyncMock(return_value=mock_create_result)

        created_media = await repository.create(media_in=create_media_in)

        assert created_media is not None
        assert created_media.name == "First Media"

        # 2. Read
        mock_read_result = MagicMock()
        mock_read_result.scalar_one_or_none.return_value = created_media
        mock_async_session.execute = AsyncMock(return_value=mock_read_result)

        retrieved_media = await repository.get_by_id(media_id=created_media.id)

        assert retrieved_media is not None
        assert retrieved_media.name == "First Media"

        # 3. Update
        update_media_in = MediaUpdate(name="Updated Media")
        mock_update_result = MagicMock()
        mock_update_result.scalar_one_or_none.return_value = created_media
        mock_async_session.execute = AsyncMock(return_value=mock_update_result)

        updated_media = await repository.update(db_media=created_media, media_in=update_media_in)

        assert updated_media.name == "Updated Media"
        assert updated_media.updated_on is not None

        # 4. Delete
        mock_delete_result = MagicMock()
        mock_async_session.execute = AsyncMock(return_value=mock_delete_result)

        await repository.delete(db_media=created_media)

        assert mock_async_session.delete.called
        assert mock_async_session.commit.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
