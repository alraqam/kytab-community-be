from datetime import datetime

from pydantic import BaseModel


class GetClubSummary(BaseModel):
    """Response payload representing a member-facing summary of a club's activity."""

    club_id: int
    club_name: str
    member_count: int
    latest_post_title: str | None = None
    latest_post_created_at: datetime | None = None
    latest_post_author_username: str | None = None
    next_event_title: str | None = None
    next_event_start_at: datetime | None = None
