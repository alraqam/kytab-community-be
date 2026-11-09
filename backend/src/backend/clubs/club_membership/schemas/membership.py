from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MemberRole(str, Enum):
    """Roles a user can hold within a club."""

    member = "member"
    club_owner = "club_owner"
    club_moderator = "club_moderator"

class InvitationStatus(str, Enum):
    """Lifecycle states of a club invitation."""

    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"

class JoinRequestStatus(str, Enum):
    """Lifecycle states of a club join request."""

    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"

class GetMembership(BaseModel):
    """Response payload representing a club membership."""

    id: int
    club_id: int
    club_name: str | None = None
    user_id: int
    username: str | None = None
    role: MemberRole
    created_at: datetime

class UpdateMemberRole(BaseModel):
    """Request payload for changing a member's role."""

    role: MemberRole

class ManageMember(BaseModel):
    """Request payload identifying a member to act on (e.g. kick)."""

    member_id: int

class SendInvitation(BaseModel):
    """Request payload for inviting a user to a club."""

    club_id: int
    user_id: int

class GetInvitation(BaseModel):
    """Response payload representing a club invitation."""

    id: int
    club_id: int
    club_name: str | None = None
    invited_by_id: int
    invited_by_username: str | None = None
    invited_user_id: int
    invited_user_username: str | None = None
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

class SendJoinRequest(BaseModel):
    """Request payload for requesting to join a club."""

    club_id: int

class GetJoinRequest(BaseModel):
    """Response payload representing a club join request."""

    id: int
    club_id: int
    club_name: str | None = None
    user_id: int
    username: str | None = None
    status: JoinRequestStatus
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

class CreateBlockedMember(BaseModel):
    """Request payload for blocking a user from a club."""

    user_id: int

class GetBlockedMember(BaseModel):
    """Response payload representing a blocked club member."""

    id: int
    user_id: int
    username: str | None = None
    club_id: int
    club_name: str | None = None

class InvitationEmail(BaseModel):
    """Request payload carrying a club invite email token."""

    token: str