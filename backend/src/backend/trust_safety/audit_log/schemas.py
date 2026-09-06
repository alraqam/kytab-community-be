from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AuditLogAction(str, Enum):
    """Moderation and administrative actions recorded in the audit log."""

    complaint_resolved = "complaint_resolved"
    complaint_dismissed = "complaint_dismissed"
    complaint_content_removed = "complaint_content_removed"
    complaint_target_warned = "complaint_target_warned"
    complaint_target_suspended = "complaint_target_suspended"
    complaint_target_banned = "complaint_target_banned"
    complaint_escalated = "complaint_escalated"

class GetAuditLog(BaseModel):
    """Response payload representing an audit log entry."""

    id: int
    actor_id: int | None = None
    actor_username: str | None = None
    action: AuditLogAction
    object_type: str
    object_id: int
    details: str | None = None
    created_at: datetime
