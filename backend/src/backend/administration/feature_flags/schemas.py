from datetime import datetime

from pydantic import BaseModel, Field


class CreateFeatureFlag(BaseModel):
    """Request payload for creating a new feature flag."""

    key: str = Field(max_length=100)
    name: str = Field(max_length=255)
    description: str | None = None
    rollout_percentage: int = Field(default=100, ge=0, le=100)

class UpdateFeatureFlag(BaseModel):
    """Request payload for updating a feature flag's name, description, and/or rollout percentage."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    rollout_percentage: int | None = Field(default=None, ge=0, le=100)

class GetFeatureFlag(BaseModel):
    """Response payload representing a feature flag."""

    id: int
    created_by_id: int
    created_by_username: str | None = None
    key: str
    name: str
    description: str | None = None
    is_enabled: bool
    rollout_percentage: int
    created_at: datetime
