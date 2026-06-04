"""Feature flag request schemas."""

from pydantic import BaseModel, Field


class FeatureFlagUpdateRequest(BaseModel):
    """Request body for updating a feature flag."""

    is_enabled: bool = Field(default=True)
