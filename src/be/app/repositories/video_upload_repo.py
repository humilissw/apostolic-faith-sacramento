from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import VideoUpload
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate
from datetime import datetime, timezone


class VideoUploadRepository:
    """
    Repository for VideoUpload entity operations.
    Handles all database interactions for video upload entries.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, video_upload_in: VideoUploadCreate, owner_id: str) -> VideoUpload:
        """
        Create a new video upload entry.

        Args:
            video_upload_in: VideoUploadCreate object containing upload data
            owner_id: ID of the user creating the upload

        Returns:
            VideoUpload: Created video upload object
        """
        video_upload = VideoUpload(
            owner_id=owner_id,
            upload_location=video_upload_in.upload_location,
            upload_name=video_upload_in.upload_name,
            description=video_upload_in.description,
            media_association_date=video_upload_in.media_association_date,
            speaker_name=video_upload_in.speaker_name,
            reference_text=video_upload_in.reference_text,
            created_on=datetime.now(timezone.utc),
            updated_on=datetime.now(timezone.utc),
        )
        self.session.add(video_upload)
        await self.session.commit()
        await self.session.refresh(video_upload)
        return video_upload

    async def get_by_id(self, video_upload_id: str) -> VideoUpload | None:
        """
        Retrieve a video upload entry by ID.

        Args:
            video_upload_id: UUID string of the video upload

        Returns:
            VideoUpload | None: VideoUpload object if found, None otherwise
        """
        statement = select(VideoUpload).where(
            VideoUpload.id == video_upload_id  # type: ignore[arg-type]
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[VideoUpload], int]:
        """
        Retrieve all video upload entries with pagination.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)

        Returns:
            tuple[list[VideoUpload], int]: Tuple of (video uploads list, total count)
        """
        # Get total count
        count_statement = select(func.count()).select_from(VideoUpload)
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar()

        # Get paginated results
        statement = select(VideoUpload).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        video_uploads = result.scalars().all()

        return list(video_uploads), total_count or 0

    async def update(
        self, db_video_upload: VideoUpload, video_upload_in: VideoUploadUpdate
    ) -> VideoUpload:
        """
        Update an existing video upload entry.

        Args:
            db_video_upload: VideoUpload object to update
            video_upload_in: VideoUploadUpdate object with update data

        Returns:
            VideoUpload: Updated video upload object
        """
        update_data = video_upload_in.model_dump(exclude_unset=True)
        update_data["updated_on"] = datetime.now(timezone.utc)

        # Handle datetime fields - remove created_on if present
        if "created_on" in update_data:
            del update_data["created_on"]

        db_video_upload.sqlmodel_update(update_data)
        self.session.add(db_video_upload)
        await self.session.commit()
        await self.session.refresh(db_video_upload)
        return db_video_upload

    async def delete(self, db_video_upload: VideoUpload) -> None:
        """
        Delete a video upload entry.

        Args:
            db_video_upload: VideoUpload object to delete
        """
        await self.session.delete(db_video_upload)
        await self.session.commit()
