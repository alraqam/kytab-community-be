from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RSVPStatus(str, Enum):
    """Possible responses a user can give to a club event RSVP."""

    yes = "yes"
    no = "no"
    maybe = "maybe"

class CreateClubEvent(BaseModel):
    """Request payload for creating a new club event."""

    title: str = Field(max_length=100)
    description: str | None = Field(max_length=512)
    start_at: datetime
    end_at: datetime
    timezone: str = Field(max_length=50)
    location_text: str  | None = Field(max_length=100)
    meeting_url: str  | None = Field(max_length=100)

class UpdateClubEvent(BaseModel):
    """Request payload for updating a club event's fields."""

    title: str | None = Field(max_length=100)
    description: str | None  = Field(max_length=512)
    start_at: datetime | None
    end_at: datetime | None
    timezone: str | None = Field(max_length=50)
    location_text: str | None = Field(max_length=100)
    meeting_url: str | None = Field(max_length=100)

class GetClubEvent(BaseModel):
    """Response payload representing a club event."""

    id: int
    club_id: int
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime
    timezone: str
    location_text: str | None = None
    meeting_url: str | None = None
    created_by_id: int
    created_by_username: str | None = None
    created_at: datetime
    updated_at: datetime


class CreateEventRSVP(BaseModel):
    """Request payload for RSVPing to a club event."""

    status: RSVPStatus

class GetEventRSVP(BaseModel):
    """Response payload representing a user's RSVP to a club event."""

    id: int
    event_id: int
    user_id: int
    username: str | None = None
    response: RSVPStatus
    created_at: datetime