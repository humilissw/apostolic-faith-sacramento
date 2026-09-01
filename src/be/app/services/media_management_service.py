"""Service for media management operations."""

from app.models import Message
from app.repositories.media_repo import MediaRepository
from app.responses.media_response import MediaPublic


class MediaManagementService:
    """Handles business logic for media management operations."""

    def __init__(self, session):
        self.session = session

    async def get_all_media(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        """Get all media entries with pagination."""
        repository = MediaRepository(session=self.session)
        medias, total_count = await repository.get_all(skip=skip, limit=limit)

        # Add download URLs (placeholder - should be implemented based on storage)
        media_data = [
            {
                "id": m.id,
                "name": m.name,
                "uploaded_on": m.uploaded_on,
                "created_on": m.created_on,
                "updated_on": m.updated_on,
                "download_url": f"/media/{m.id}/download",
            }
            for m in medias
        ]

        return media_data, total_count

    async def get_media_by_id(self, media_id: str) -> MediaPublic | None:
        """Get media by ID."""
        repository = MediaRepository(session=self.session)
        media = await repository.get_by_id(media_id=media_id)
        if not media:
            return None

        return MediaPublic(
            id=media.id,
            name=media.name,
            uploaded_on=media.uploaded_on,
            created_on=media.created_on,
            updated_on=media.updated_on,
        )

    async def update_media(self, media_id: str, current_user, media_in) -> MediaPublic | None:
        """Update a media entry (requires ownership or superuser)."""
        repository = MediaRepository(session=self.session)
        media = await repository.get_by_id(media_id=media_id)
        if not media:
            return None
        if current_user.id != media.owner_id and not current_user.is_superuser:
            raise PermissionError("Not authorized to update this media")

        media = await repository.update(db_media=media, media_in=media_in)
        return MediaPublic(
            id=media.id,
            name=media.name,
            uploaded_on=media.uploaded_on,
            created_on=media.created_on,
            updated_on=media.updated_on,
        )

    async def delete_media(self, media_id: str, current_user) -> Message | None:
        """Delete a media entry (requires ownership or superuser)."""
        repository = MediaRepository(session=self.session)
        media = await repository.get_by_id(media_id=media_id)
        if not media:
            return None
        if current_user.id != media.owner_id and not current_user.is_superuser:
            raise PermissionError("Not authorized to delete this media")

        await repository.delete(db_media=media)
        return Message(message="Media deleted successfully")
