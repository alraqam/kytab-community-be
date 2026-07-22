from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateWork(BaseModel):
    """Request payload for creating a new work."""

    canonical_title: str = Field(max_length=512)
    description: str | None = None
    primary_language: str | None = Field(default=None, max_length=100)

class UpdateWork(BaseModel):
    """Request payload for updating work details."""

    canonical_title: str | None = Field(default=None, max_length=512)
    description: str | None = None
    primary_language: str | None = Field(default=None, max_length=100)

class GetWork(BaseModel):
    """Work data returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    canonical_title: str
    description: str | None
    primary_language: str | None
    created_at: datetime
    updated_at: datetime
