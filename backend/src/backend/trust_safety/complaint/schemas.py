from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ComplaintObjectType(str, Enum):
    """Types of entities a complaint can be filed against."""

    review = "review"
    comment = "comment"
    post = "post"
    club = "club"
    user = "user"

class ComplaintCategory(str, Enum):
    """Reasons a complaint can be filed for."""

    spam = "spam"
    abuse = "abuse"
    inappropriate = "inappropriate"
    other = "other"

class ComplaintStatus(str, Enum):
    """Moderation lifecycle states of a complaint."""

    pending = "pending"
    reviewed = "reviewed"
    dismissed = "dismissed"

class CreateComplaint(BaseModel):
    """Request payload for filing a complaint against a piece of content or a user."""

    object_type: ComplaintObjectType
    object_id: int
    category: ComplaintCategory
    comment: str = Field(max_length=500)

class WarnComplaintTarget(BaseModel):
    """Request payload for sending a moderation warning to a complaint's target user."""

    message: str = Field(max_length=500)

class GetComplaint(BaseModel):
    """Response payload representing a complaint."""

    id: int
    reporter_id: int
    reporter_username: str | None = None
    object_type: str
    object_id: int
    category: str
    comment: str | None = None
    status: str
    is_escalated: bool
    resolved_by_id: int | None = None
    resolved_by_username: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None
