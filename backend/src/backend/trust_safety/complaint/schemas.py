from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ComplaintObjectType(str, Enum):
    review = "review"
    comment = "comment"
    club = "club"
    user = "user"

class ComplaintCategory(str, Enum):
    spam = "spam"
    abuse = "abuse"
    inappropriate = "inappropriate"
    other = "other"

class ComplaintStatus(str, Enum):
    pending = "pending"
    reviewed = "reviewed"
    dismissed = "dismissed"

class CreateComplaint(BaseModel):
    object_type: ComplaintObjectType
    object_id: int
    category: ComplaintCategory
    comment: str = Field(max_length=500)

class GetComplaint(BaseModel):
    id: int
    reporter_id: int
    object_type: str
    object_id: int
    category: str
    comment: str | None = None
    status: str
    resolved_by_id: int | None = None
    created_at: datetime
    resolved_at: datetime | None = None
