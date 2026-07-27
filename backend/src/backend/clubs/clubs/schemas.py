from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ClubTypes(str, Enum):
    public = "public"
    private = "private"
    secret = "secret"

class ClubPublicTypes(str, Enum):
    public = "public"
    private = "private"

class CreateClub(BaseModel):
    name: str = Field(max_length=256)
    description: str | None = Field(max_length=1024)

class UpdateClub(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)
    club_type: ClubTypes | None = None
    cover: str | None = None
    language: str | None = None

class AddClubGenre(BaseModel):
    club_id: int
    genre_id: int

class ManageClubModerators(BaseModel):
    user_id: int

class GetClub(BaseModel):
    id: int
    name: str
    description: str | None
    club_type: ClubTypes
    cover: str | None = None
    language: str | None = None
    owner_id: int
    is_archived: bool
    created_at: datetime



