from pydantic import BaseModel, ConfigDict, Field


class CreateAuthor(BaseModel):
    """Request payload for creating a new author."""

    name: str = Field(max_length=512)
    bio: str | None = None
    photo_url: str | None = None

class UpdateAuthor(BaseModel):
    """Request payload for updating author details."""

    name: str | None = Field(default=None, max_length=512)
    bio: str | None = None
    photo_url: str | None = None

class GetAuthor(BaseModel):
    """Author data returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bio: str | None
    photo_url: str | None

class AddAuthorToWork(BaseModel):
    """Request payload for linking an author to a work."""

    work_id: int
    author_id: int
    order: int | None = None
