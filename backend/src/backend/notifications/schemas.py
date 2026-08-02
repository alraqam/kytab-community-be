from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class NotificationCategory(str, Enum):
    club_invite = "club_invite"
    join_approval = "join_approval"
    mention = "mention"
    event_reminder = "event_reminder"
    poll_opening = "poll_opening"
    poll_closing = "poll_closing"
    milestone_date_reached = "milestone_date_reached"
    general = "general"

class NotificationObjectType(str, Enum):
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
    none = "none"
    daily = "daily"
    weekly = "weekly"

class GetNotification(BaseModel):
    id: int
    user_id: int
    club_id: int | None = None
    category: NotificationCategory
    title: str
    body: str | None = None
    object_type: NotificationObjectType | None = None
    object_id: int | None = None
    is_read: bool
    created_at: datetime

class CreateNotificationPreference(BaseModel):
    club_id: int | None = None
    category: NotificationCategory
    in_app_enabled: bool = True
    email_enabled: bool = True
    push_enabled: bool = False
    digest_frequency: DigestFrequency = DigestFrequency.none

class UpdateNotificationPreference(BaseModel):
    in_app_enabled: bool | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    digest_frequency: DigestFrequency | None = None

class GetNotificationPreference(BaseModel):
    id: int
    user_id: int
    club_id: int | None = None
    category: NotificationCategory
    in_app_enabled: bool
    email_enabled: bool
    push_enabled: bool
    digest_frequency: DigestFrequency
    is_muted: bool
    created_at: datetime
    updated_at: datetime | None = None
