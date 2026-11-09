from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class FeedItemType(str, Enum):
    """Kinds of activity that can appear in a user's home feed."""

    review = "review"
    club = "club"

class FeedItem(BaseModel):
    """Response payload representing a single item in a user's home feed."""

    type: FeedItemType
    created_at: datetime
    actor_id: int | None = None
    actor_username: str | None = None
    club_id: int | None = None
    club_name: str | None = None
    review_id: int | None = None
    work_id: int | None = None
    work_title: str | None = None
    rating: float | None = None
    body: str | None = None
