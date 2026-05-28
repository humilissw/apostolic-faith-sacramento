"""Feature flag response schemas."""

from pydantic import BaseModel


class FeatureFlagUpdateResponse(BaseModel):
    """Response after updating a feature flag."""

    model_config = {"from_attributes": True}
    id: str
    name: str
    description: str
    is_enabled: bool
    created_on: str
    updated_on: str | None
