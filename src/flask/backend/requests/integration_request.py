"""Request schemas for integration configs."""

from pydantic import BaseModel, Field


class IntegrationCreate(BaseModel):
    type: str = Field(..., max_length=50)
    display_name: str = Field(..., max_length=100)
    icon: str = Field(default="Plug", max_length=50)
    enabled: bool = False
    config_json: str | None = Field(default=None, max_length=4000)
    credentials: dict[str, str] = Field(default_factory=dict)


class IntegrationUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    icon: str | None = Field(default=None, max_length=50)
    enabled: bool | None = None
    status: str | None = Field(default=None, max_length=20)
    config_json: str | None = Field(default=None, max_length=4000)


class CredentialUpdate(BaseModel):
    credentials: dict[str, str]


class TestConnectionRequest(BaseModel):
    type: str = Field(..., max_length=50)
    credentials: dict[str, str] = Field(default_factory=dict)
    config_json: str | None = Field(default=None, max_length=4000)
