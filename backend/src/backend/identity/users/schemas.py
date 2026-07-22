from datetime import datetime

from pydantic import BaseModel

from src.backend.identity.auth.schemas import UserRoleEnum


class UpdateUserRole(BaseModel):
    """Request payload for changing a user's system-level role (admin actions)."""

    role: UserRoleEnum

class UpdateUserActivity(BaseModel):
    """Request payload for activating or deactivating a user account (admin actions)."""

    is_active: bool

class UpdateUserVerification(BaseModel):
    is_verified: bool


class GetAdminUser(BaseModel):
    """Response schema for admin user list — excludes sensitive fields like hashed_password."""

    id: int
    email: str
    username: str
    role: str
    is_active: bool
    is_verified: bool
    is_deleted: bool
    deleted_at: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True

