from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ProfileVisibilityEnum(str, Enum):
    public = "public"
    private = "private"
    followers_only = "followers_only"

class CreateProfile(BaseModel):
    user_id: int
    fullname: str

class UpdateProfileAvatar(BaseModel):
    """Request payload for updating the user's avatar with a URL."""

    avatar_url: str  = Field(max_length=500)

class UpdateProfile(BaseModel):
    fullname: str  | None = Field(max_length=512)
    bio: str  | None = Field(max_length=1024)
    favorite_genres: list[str]  | None
    links: list[str]  | None

class UpdateProfileVisibility(BaseModel):
    visibility: ProfileVisibilityEnum

class GetProfile(BaseModel):
    user_id: int
    fullname: str | None = None
    bio: str | None = None
    avatar: str | None = None
    favorite_genres: list[str] | None = None
    links: list[str] | None = None
    visibility: str
    created_at: datetime

