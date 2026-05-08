"""Response schemas for integration configs."""

from datetime import datetime

from pydantic import BaseModel


class IntegrationConfigPublic(BaseModel):
    id: str
    type: str
    display_name: str
    icon: str
    enabled: bool
    status: str
    last_synced_at: datetime | None
    config_json: str | None
    created_on: datetime
    updated_on: datetime | None


class IntegrationConfigPublicWithCreds(IntegrationConfigPublic):
    credential_fields: dict[str, str] = {}


class IntegrationsPublic(BaseModel):
    data: list[IntegrationConfigPublic]
    count: int


class TestConnectionResponse(BaseModel):
    success: bool
    status: str
    message: str = ""
