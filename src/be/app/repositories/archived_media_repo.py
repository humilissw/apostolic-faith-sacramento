from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ArchivedMedia
from datetime import datetime, timezone
from app.config import settings



class ArchivedMediaRepository:
    """
    Repository for ArchivedMedia entity operations.
    Handles all database interactions for media archives.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session


    async def get_by_id(self, archived_media_id: str) -> ArchivedMedia | None:
        """
        Retrieve a media archive entry by ID.

        Args:
            archived_media_id: UUID string of the video upload

        Returns:
            ArchivedMedia | None: ArchivedMedia object if found, None otherwise
        """
        statement = select(ArchivedMedia).where(
            ArchivedMedia.id == archived_media_id  # type: ignore[arg-type]
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[ArchivedMedia], int]:
        """
        Retrieve all archived media entries with pagination.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)

        Returns:
            tuple[list[ArchivedMedia], int]: Tuple of (archived media list, total count)
        """
        # Get total count
        count_statement = select(func.count()).select_from(ArchivedMedia)
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar()

        # Get paginated results
        statement = select(ArchivedMedia).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        video_uploads = result.scalars().all()

        return list(video_uploads), total_count or 0

    # async def update(
    #     self, db_video_upload: VideoUpload, video_upload_in: VideoUploadUpdate
    # ) -> VideoUpload:
    #     """
    #     Update an existing video upload entry.

    #     Args:
    #         db_video_upload: VideoUpload object to update
    #         video_upload_in: VideoUploadUpdate object with update data

    #     Returns:
    #         VideoUpload: Updated video upload object
    #     """
    #     update_data = video_upload_in.model_dump(exclude_unset=True)
    #     update_data["updated_on"] = datetime.now(timezone.utc)

    #     # Handle datetime fields - remove created_on if present
    #     if "created_on" in update_data:
    #         del update_data["created_on"]

    #     db_video_upload.sqlmodel_update(update_data)
    #     self.session.add(db_video_upload)
    #     await self.session.commit()
    #     await self.session.refresh(db_video_upload)
    #     return db_video_upload

    async def delete(self, db_archived_media: ArchivedMedia) -> None:
        """
        Delete an archived media entry.

        Args:
            db_archived_media: ArchivedMedia object to delete
        """
        await self.session.delete(db_archived_media)
        await self.session.commit()
