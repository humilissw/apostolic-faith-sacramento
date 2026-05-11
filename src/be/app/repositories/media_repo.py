from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models import Media
from app.requests.media_request import MediaCreate, MediaUpdate
from datetime import datetime, timezone


class MediaRepository:
    """
    Repository for Media entity operations.
    Handles all database interactions for media entries.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, media_in: MediaCreate, owner_id: str) -> Media:
        """
        Create a new media entry.

        Args:
            media_in: MediaCreate object containing media data
            owner_id: ID of the user creating the media

        Returns:
            Media: Created media object
        """
        try:
            media = Media(
                name=media_in.name,
                owner_id=owner_id,
                uploaded_on=datetime.now(timezone.utc),
                created_on=datetime.now(timezone.utc),
                updated_on=datetime.now(timezone.utc),
            )
            self.session.add(media)
            await self.session.commit()
            await self.session.refresh(media)
            return media
        except Exception:
            raise HTTPException(
                status_code=500, detail="Database error occurred while creating media"
            )

    async def get_by_id(self, media_id: str) -> Media | None:
        """
        Retrieve a media entry by ID.

        Args:
            media_id: UUID string of the media entry

        Returns:
            Media | None: Media object if found, None otherwise
        """
        try:
            statement = select(Media).where(Media.id == media_id)  # type: ignore[arg-type]
            result = await self.session.execute(statement)
            return result.scalar_one_or_none()  # type: ignore[no-any-return]
        except Exception:
            raise HTTPException(
                status_code=500, detail="Database error occurred while retrieving media"
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Media], int]:
        """
        Retrieve all media entries with pagination.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)

        Returns:
            tuple[list[Media], int]: Tuple of (media list, total count)
        """
        try:
            # Get total count
            count_statement = select(func.count()).select_from(Media)
            count_result = await self.session.execute(count_statement)
            total_count = count_result.scalar()
        except Exception:
            raise HTTPException(
                status_code=500, detail="Database error occurred while counting media"
            )

        try:
            # Get paginated results
            statement = select(Media).offset(skip).limit(limit)
            result = await self.session.execute(statement)
            medias = result.scalars().all()
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while retrieving media list",
            )

        return list(medias), total_count or 0

    async def update(self, db_media: Media, media_in: MediaUpdate) -> Media:
        """
        Update an existing media entry.

        Args:
            db_media: Media object to update
            media_in: MediaUpdate object with update data

        Returns:
            Media: Updated media object
        """
        # Check if media exists
        if db_media is None:
            raise HTTPException(status_code=404, detail="Media not found")

        update_data = media_in.model_dump(exclude_unset=True)
        update_data["updated_on"] = datetime.now(timezone.utc)

        # Handle datetime fields - remove created_on if present
        if "created_on" in update_data:
            del update_data["created_on"]

        db_media.sqlmodel_update(update_data)
        self.session.add(db_media)
        await self.session.commit()
        await self.session.refresh(db_media)
        return db_media

    async def delete(self, db_media: Media) -> None:
        """
        Delete a media entry.

        Args:
            db_media: Media object to delete
        """
        # Check if media exists in the database
        if db_media is None:
            return

        # Delete the media directly
        await self.session.delete(db_media)
        await self.session.commit()
