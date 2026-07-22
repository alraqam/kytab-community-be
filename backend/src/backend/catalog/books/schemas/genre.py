from pydantic import BaseModel, ConfigDict, Field


class CreateGenre(BaseModel):
    """Request payload for creating a new genre."""

    name: str = Field(max_length=512)
    slug: str = Field(max_length=512)

class UpdateGenre(BaseModel):
    """Request payload for updating genre details."""

    name: str | None = Field(default=None, max_length=512)
    slug: str | None = Field(default=None, max_length=512)

class GetGenre(BaseModel):
    """Genre data returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str

class AddGenreToWork(BaseModel):
    """Request payload for linking a genre to a work."""

    work_id: int
    genre_id: int
