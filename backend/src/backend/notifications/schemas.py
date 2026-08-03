from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class NotificationCategory(str, Enum):
    """Categories of events that can trigger a notification."""

    club_invite = "club_invite"
    join_approval = "join_approval"
    mention = "mention"
    event_reminder = "event_reminder"
    poll_opening = "poll_opening"
    poll_closing = "poll_closing"
    milestone_date_reached = "milestone_date_reached"
    general = "general"

class NotificationObjectType(str, Enum):
    """Types of entities a notification can reference via object_type/object_id."""

    club = "club"
    invitation = "invitation"
    join_request = "join_request"
    post = "post"
    comment = "comment"
    poll = "poll"
    event = "event"
    milestone = "milestone"
    complaint = "complaint"

class DigestFrequency(str, Enum):
    """How often a digest of notifications should be sent for a preference."""

    none = "none"
    daily = "daily"
    weekly = "weekly"

class GetNotification(BaseModel):
    """Response payload representing a notification."""

    id: int
    user_id: int
    username: str | None = None
    club_id: int | None = None
    club_name: str | None = None
    category: NotificationCategory
    title: str
    body: str | None = None
    object_type: NotificationObjectType | None = None
    object_id: int | None = None
    is_read: bool
    created_at: datetime

class CreateNotificationPreference(BaseModel):
    """Request payload for creating a notification preference for a category, optionally scoped to a club."""

    club_id: int | None = None
    category: NotificationCategory
    in_app_enabled: bool = True
    email_enabled: bool = True
    push_enabled: bool = False
    digest_frequency: DigestFrequency = DigestFrequency.none

class UpdateNotificationPreference(BaseModel):
    """Request payload for updating a notification preference's delivery channels and digest frequency."""

    in_app_enabled: bool | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    digest_frequency: DigestFrequency | None = None

class GetNotificationPreference(BaseModel):
    """Response payload representing a notification preference."""

    id: int
    user_id: int
    username: str | None = None
    club_id: int | None = None
    club_name: str | None = None
    category: NotificationCategory
    in_app_enabled: bool
    email_enabled: bool
    push_enabled: bool
    digest_frequency: DigestFrequency
    is_muted: bool
    created_at: datetime
    updated_at: datetime | None = None
