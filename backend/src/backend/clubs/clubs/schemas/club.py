from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.backend.catalog.books.schemas.genre import GetGenre
from src.backend.clubs.clubs.models.club import Club, DEFAULT_CLUB_MEMBER_CAP


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
    # Optional; shown only to platform staff (admins and platform moderators).
    opening_reason: str | None = Field(default=None, max_length=1024)

class UpdateClub(BaseModel):
    """Request payload for updating a club's details."""

    name: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)
    club_type: ClubTypes | None = None
    language: str | None = None
    # Raising the cap beyond the platform default is a future premium lever (FR-CLB-23);
    # for now owners/moderators may only lower it, not raise it.
    member_cap: int | None = Field(default=None, ge=1, le=DEFAULT_CLUB_MEMBER_CAP)

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
    owner_username: str | None = None
    genres: list[GetGenre] = []
    is_archived: bool
    member_cap: int
    member_count: int = 0
    created_at: datetime

class ClubCurrentBook(BaseModel):
    """A book a club is currently reading (one per active reading session)."""

    session_id: int
    work_id: int
    title: str | None = None
    deadline: datetime

class GetClubPreview(BaseModel):
    """Limited view of a club shown before joining (FR-CLB-04): name, description, member count, and current book(s)."""

    id: int
    name: str
    description: str | None
    club_type: ClubTypes
    member_count: int
    current_books: list[ClubCurrentBook] = []

class GetAdminClub(GetClub):
    """Response payload representing a club for platform staff, including staff-only fields."""

    opening_reason: str | None = None
    platform_manager_id: int | None = None
    platform_manager_username: str | None = None

class AssignPlatformManager(BaseModel):
    """Request payload for manually assigning a club to a platform moderator."""

    user_id: int

class GetPlatformManagerLoad(BaseModel):
    """A platform moderator and the number of active (non-archived) clubs assigned to them."""

    manager_id: int
    username: str
    active_clubs: int

class AssignUnassignedClubsResult(BaseModel):
    """Result of assigning clubs that had no platform moderator."""

    assigned: int

def to_get_admin_club(club: Club, cover_url: str | None) -> GetAdminClub:
    """Builds a GetAdminClub response with the stored cover key replaced by a presigned URL.

    Args:
        club: Club instance to serialize.
        cover_url: Presigned URL to expose in place of the stored cover key.

    Returns:
        GetAdminClub response payload.
    """
    result = GetAdminClub.model_validate(club, from_attributes=True)
    result.cover = cover_url
    result.member_count = len(club.members)
    return result

def to_get_club(club: Club, cover_url: str | None) -> GetClub:
    """Builds a GetClub response with the stored cover key replaced by a presigned URL.

    Args:
        club: Club instance to serialize.
        cover_url: Presigned URL to expose in place of the stored cover key.

    Returns:
        GetClub response payload.
    """
    result = GetClub.model_validate(club, from_attributes=True)
    result.cover = cover_url
    result.member_count = len(club.members)
    return result

