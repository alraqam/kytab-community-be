from datetime import datetime

from pydantic import BaseModel, Field


class CreateAnnouncement(BaseModel):
    title: str = Field(max_length=255)
    body: str

class UpdateAnnouncement(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    body: str | None = None

class GetAnnouncement(BaseModel):
    id: int
    created_by_id: int
    title: str
    body: str
    is_published: bool
    published_at: datetime | None = None
    created_at: datetime
