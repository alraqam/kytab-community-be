from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.backend.catalog.books.schemas.author import GetAuthor
from src.backend.catalog.books.schemas.genre import GetGenre
from src.backend.catalog.books.schemas.series import GetSeries


class CreateWork(BaseModel):
    """Request payload for creating a new work."""

    canonical_title: str = Field(max_length=512)
    description: str | None = None
    primary_language: str | None = Field(default=None, max_length=100)

class UpdateWork(BaseModel):
    """Request payload for updating work details."""

    canonical_title: str | None = Field(default=None, max_length=512)
    description: str | None = None
    primary_language: str | None = Field(default=None, max_length=100)

class MergeWork(BaseModel):
    """Request payload for merging a duplicate work into this work."""

    source_work_id: int

class GetWork(BaseModel):
    """Work data returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    canonical_title: str
    description: str | None
    primary_language: str | None
    cover_url: str | None = None
    authors: list[GetAuthor] = []
    genres: list[GetGenre] = []
    series: list[GetSeries] = []
    created_at: datetime
    updated_at: datetime
