from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RSVPStatus(str, Enum):
    yes = "yes"
    no = "no"
    maybe = "maybe"

class CreateClubEvent(BaseModel):
    title: str = Field(max_length=100)
    description: str | None = Field(max_length=512)
    start_at: datetime
    end_at: datetime
    timezone: str = Field(max_length=50)
    location_text: str  | None = Field(max_length=100)
    meeting_url: str  | None = Field(max_length=100)

class UpdateClubEvent(BaseModel):
    title: str | None = Field(max_length=100)
    description: str | None  = Field(max_length=512)
    start_at: datetime | None
    end_at: datetime | None
    timezone: str | None = Field(max_length=50)
    location_text: str | None = Field(max_length=100)
    meeting_url: str | None = Field(max_length=100)

class GetClubEvent(BaseModel):
    id: int
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime
    timezone: str
    location_text: str | None = None
    meeting_url: str | None = None
    created_at: datetime
    updated_at: datetime


class CreateEventRSVP(BaseModel):
    status: RSVPStatus

class GetEventRSVP(BaseModel):
    id: int
    event_id: int
    user_id: int
    response: RSVPStatus
    created_at: datetime