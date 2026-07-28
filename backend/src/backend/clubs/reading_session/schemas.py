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
    work_id: int
    deadline: datetime
    status: ReadingSessionStatus
    created_by_id: int
    completed_at: datetime | None
    created_at: datetime

class MilestoneBoundaryType(str, Enum):
    page = "page"
    chapter = "chapter"
    percent = "percent"

class BaseMilestone(BaseModel):
    label: str
    boundary_type: MilestoneBoundaryType
    boundary_value: str
    target_date: date
    order_index: int

class CreateMilestone(BaseMilestone):
    pass

class UpdateMilestone(BaseMilestone):
    pass

class GetMilestone(BaseMilestone):
    id: int
    created_at: datetime
    updated_at: datetime