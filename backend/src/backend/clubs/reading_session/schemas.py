from datetime import datetime, date
from enum import Enum

from pydantic import BaseModel


class ReadingSessionStatus(str, Enum):
    """Possible statuses of a reading session: active or completed."""

    active = "active"
    completed = "completed"

class CreateReadingSession(BaseModel):
    """Request payload for starting a new reading session in a club."""

    work_id: int
    deadline: datetime

class GetReadingSession(BaseModel):
    """Reading session data returned in API responses."""

    id: int
    club_id: int
    club_name: str | None = None
    work_id: int
    work_title: str | None = None
    deadline: datetime
    status: ReadingSessionStatus
    created_by_id: int
    created_by_username: str | None = None
    completed_at: datetime | None
    created_at: datetime

class MilestoneBoundaryType(str, Enum):
    """Possible boundary types for a milestone: page, chapter, or percent."""

    page = "page"
    chapter = "chapter"
    percent = "percent"

class CreateMilestone(BaseModel):
    """Request payload for creating a new milestone within a reading session."""

    label: str
    boundary_type: MilestoneBoundaryType
    boundary_value: int
    target_date: date
    order_index: int

class UpdateMilestone(BaseModel):
    """Request payload for updating a milestone's fields."""

    label: str | None = None
    boundary_type: MilestoneBoundaryType | None = None
    boundary_value: int | None = None
    target_date: date | None = None
    order_index: int | None = None


class GetMilestone(BaseModel):
    """Milestone data returned in API responses."""

    id: int
    session_id: int
    label: str
    boundary_type: MilestoneBoundaryType
    boundary_value: int
    target_date: date
    order_index: int
    created_at: datetime
    updated_at: datetime

class GetMilestoneProgress(BaseModel):
    """Milestone progress data returned in API responses."""

    id: int
    session_id: int
    milestone_id: int
    milestone_label: str | None = None
    user_id: int
    username: str | None = None
    is_finished: bool
    created_at: datetime
    updated_at: datetime

class CreateDiscussionPrompt(BaseModel):
    """Request payload for creating a new discussion prompt on a milestone."""

    text: str

class UpdateDiscussionPrompt(BaseModel):
    """Request payload for updating a discussion prompt's text."""

    text: str | None = None

class GetDiscussionPrompt(BaseModel):
    """Discussion prompt data returned in API responses."""

    id: int
    milestone_id: int
    milestone_label: str | None = None
    created_by_id: int
    created_by_username: str | None = None
    text: str
    created_at: datetime
    updated_at: datetime