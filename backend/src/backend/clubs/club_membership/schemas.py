from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MemberRole(str, Enum):
    member = "member"
    club_owner = "club_owner"
    club_moderator = "club_moderator"

class InvitationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"

class JoinRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"

class GetMembership(BaseModel):
    id: int
    club_id: int
    user_id: int
    role: MemberRole
    created_at: datetime

class UpdateMemberRole(BaseModel):
    role: MemberRole

class ManageMember(BaseModel):
    member_id: int

class SendInvitation(BaseModel):
    club_id: int
    user_id: int

class GetInvitation(BaseModel):
    id: int
    club_id: int
    invited_by_id: int
    invited_user_id: int
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

class SendJoinRequest(BaseModel):
    club_id: int

class GetJoinRequest(BaseModel):
    id: int
    club_id: int
    user_id: int
    status: JoinRequestStatus
    expires_at: datetime
    created_at: datetime
    updated_at: datetime