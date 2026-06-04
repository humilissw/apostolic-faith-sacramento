"""Feature flag service with known flag definitions and pre-seed."""

from app.models import FeatureFlag
from app.repositories.feature_flag_repo import FeatureFlagRepository

# Known feature flags for all views
KNOWN_FEATURE_FLAGS: dict[str, dict[str, str | list[str]]] = {
    "enable_home": {
        "display_name": "Home",
        "description": "Show the home page",
        "icon": "Home",
        "required_scopes": [],
    },
    "enable_doctrines": {
        "display_name": "Doctrines",
        "description": "Show the doctrines page",
        "icon": "BookOpen",
        "required_scopes": [],
    },
    "enable_contact": {
        "display_name": "Contact",
        "description": "Show the contact page",
        "icon": "Mail",
        "required_scopes": [],
    },
    "enable_media": {
        "display_name": "Media",
        "description": "Show the media page",
        "icon": "Film",
        "required_scopes": [],
    },
    "enable_donate": {
        "display_name": "Donate",
        "description": "Show the donate page",
        "icon": "CreditCard",
        "required_scopes": [],
    },
    "enable_sermon": {
        "display_name": "Sermons",
        "description": "Show the sermon page (external YouTube)",
        "icon": "Video",
        "required_scopes": [],
    },
    "enable_live_service": {
        "display_name": "Live Service",
        "description": "Show the live service page",
        "icon": "Broadcast",
        "required_scopes": [],
    },
    "enable_video_uploads": {
        "display_name": "Video Uploads",
        "description": "Show the video uploads page",
        "icon": "Video",
        "required_scopes": ["authenticated"],
    },
    "enable_scheduler_calendar": {
        "display_name": "Scheduler Calendar",
        "description": "Show the scheduler calendar",
        "icon": "Calendar",
        "required_scopes": ["scheduler:admin", "member:limited"],
    },
    "enable_scheduler_admin": {
        "display_name": "Scheduler Admin",
        "description": "Show the scheduler admin page",
        "icon": "Calendar",
        "required_scopes": ["scheduler:admin"],
    },
    "enable_my_scheduler": {
        "display_name": "My Scheduler",
        "description": "Show the my scheduler page",
        "icon": "Calendar",
        "required_scopes": ["scheduler:admin", "member:limited"],
    },
    "enable_users_admin": {
        "display_name": "Users Admin",
        "description": "Show the users admin page",
        "icon": "Users",
        "required_scopes": ["superuser"],
    },
    "enable_video_uploads_admin": {
        "display_name": "Video Uploads Admin",
        "description": "Show the video uploads admin page",
        "icon": "Film",
        "required_scopes": ["superuser"],
    },
    "enable_integrations": {
        "display_name": "Integrations",
        "description": "Show the integrations page",
        "icon": "Settings",
        "required_scopes": ["superuser"],
    },
    "enable_flags_admin": {
        "display_name": "Flags Admin",
        "description": "Show the feature flags admin page",
        "icon": "ToggleRight",
        "required_scopes": ["superuser"],
    },
}


class FeatureFlagService:
    def __init__(self, repository: FeatureFlagRepository):
        self.repo = repository

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[FeatureFlag], int]:
        return await self.repo.get_all(skip, limit)

    async def get_by_id(self, id: str) -> FeatureFlag | None:
        return await self.repo.get_by_id(id)

    async def get_by_name(self, name: str) -> FeatureFlag | None:
        return await self.repo.get_by_name(name)

    async def get_by_names(self, names: list[str]) -> list[FeatureFlag]:
        return await self.repo.get_by_names(names)

    async def get_enabled_names(self) -> list[str]:
        return await self.repo.get_enabled_names()

    async def update_enabled(self, flag: FeatureFlag, enabled: bool) -> FeatureFlag:
        flag.is_enabled = enabled
        flag.updated_on = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        self.repo.session.add(flag)
        await self.repo.session.commit()
        await self.repo.session.refresh(flag)
        return flag

    async def pre_seed_flags(self) -> list[FeatureFlag]:
        """Create default entries for all known feature flag types if they don't exist."""
        created: list[FeatureFlag] = []

        for flag_name, meta in KNOWN_FEATURE_FLAGS.items():
            existing = await self.repo.get_by_name(flag_name)
            if not existing:
                flag = await self.repo.create(
                    {
                        "name": flag_name,
                        "description": meta["description"],
                        "is_enabled": True,
                    }
                )
                created.append(flag)

        return created
