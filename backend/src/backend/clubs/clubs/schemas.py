from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ClubTypes(str, Enum):
    """Visibility levels a club can have: public, private, or secret."""

    public = "public"
    private = "private"
    secret = "secret"

class ClubPublicTypes(str, Enum):
    """Visibility levels exposed in public club listings, excluding secret clubs."""

    public = "public"
    private = "private"

class CreateClub(BaseModel):
    """Request payload for creating a new club."""

    name: str = Field(max_length=256)
    description: str | None = Field(max_length=1024)

class UpdateClub(BaseModel):
    """Request payload for updating a club's details."""

    name: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)
    club_type: ClubTypes | None = None
    cover: str | None = None
    language: str | None = None

class AddClubGenre(BaseModel):
    """Request payload for associating a genre with a club."""

    club_id: int
    genre_id: int

class ManageClubModerators(BaseModel):
    """Request payload identifying a user to promote or transfer club ownership to."""

    user_id: int

class GetClub(BaseModel):
    """Response payload representing a club."""

    id: int
    name: str
    description: str | None
    club_type: ClubTypes
    cover: str | None = None
    language: str | None = None
    owner_id: int
    is_archived: bool
    created_at: datetime



