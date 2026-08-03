from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict


class LogProgressSchema(BaseModel):
    """Request payload for logging the number of pages read today."""

    pages: int = Field(gt=0)
    note: str | None = Field(max_length=255)

class GetProgressLog(BaseModel):
    """Daily progress log data returned in API responses."""

    id: int
    user_id: int
    username: str | None = None
    period_id: int
    pages_read: int
    log_date: date
    note: str | None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GetReadingPeriod(BaseModel):
    """Reading period data returned in API responses."""

    id: int
    shelf_item_id: int
    started_at: datetime
    finished_at: datetime | None = None


