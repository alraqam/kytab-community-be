from datetime import datetime

from pydantic import BaseModel, Field


class CreateAnnouncement(BaseModel):
    """Request payload for creating a new announcement."""

    title: str = Field(max_length=255)
    body: str

class UpdateAnnouncement(BaseModel):
    """Request payload for updating an announcement's title and/or body."""

    title: str | None = Field(default=None, max_length=255)
    body: str | None = None

class GetAnnouncement(BaseModel):
    """Response payload representing an announcement."""

    id: int
    created_by_id: int
    created_by_username: str | None = None
    title: str
    body: str
    is_published: bool
    published_at: datetime | None = None
    created_at: datetime
