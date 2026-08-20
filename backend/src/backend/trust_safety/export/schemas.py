from datetime import date, datetime

from pydantic import BaseModel


class ShelfItemExport(BaseModel):
    """Export payload representing a single shelved book."""

    shelf_name: str
    work_title: str | None = None
    edition_title: str | None = None
    added_at: datetime


class ReviewExport(BaseModel):
    """Export payload representing a single review."""

    work_title: str | None = None
    rating: float | None
    text: str | None
    contains_spoiler: bool
    created_at: datetime
    updated_at: datetime


class ReadingPeriodExport(BaseModel):
    """Export payload representing a single reading period."""

    work_title: str | None = None
    started_at: datetime | None
    finished_at: datetime | None


class ProgressLogExport(BaseModel):
    """Export payload representing a single progress log entry."""

    period_id: int
    pages_read: int
    log_date: date
    note: str | None


class ClubPostExport(BaseModel):
    """Export payload representing a single club post."""

    thread_title: str | None = None
    title: str
    body: str
    is_spoiler: bool
    created_at: datetime


class UserDataExport(BaseModel):
    """Export payload bundling all of a user's exportable personal data."""

    user_id: int
    username: str
    email: str
    generated_at: datetime
    shelf_items: list[ShelfItemExport]
    reviews: list[ReviewExport]
    reading_periods: list[ReadingPeriodExport]
    progress_logs: list[ProgressLogExport]
    club_posts: list[ClubPostExport]
