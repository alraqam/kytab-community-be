from datetime import date, datetime

from pydantic import BaseModel, Field


class LogProgressSchema(BaseModel):
    """Request payload for logging the number of pages read today."""

    pages: int = Field(gt=0)

class GetProgressLog(BaseModel):
    """Daily progress log data returned in API responses."""

    id: int
    user_id: int
    reading_period_id: int
    pages_read: int
    log_date: date
    created_at: datetime
    updated_at: datetime

class GetReadingPeriod(BaseModel):
    id: int
    shelf_item_id: int
    started_at: datetime
    finished_at: datetime


