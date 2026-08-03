from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateEdition(BaseModel):
    """Request payload for creating a new edition under a work."""

    work_id: int
    title: str = Field(max_length=512)
    language: str = Field(max_length=100)
    google_books_id: str
    open_library_id: str
    publisher: str | None = Field(default=None, max_length=512)
    published_year: int | None = None
    pages_count: int | None = None
    isbn: str | None = None
    cover_url: str | None = None
    is_primary: bool = False

class UpdateEdition(BaseModel):
    """Request payload for updating edition details."""

    title: str | None = Field(default=None, max_length=512)
    language: str | None = Field(default=None, max_length=100)
    publisher: str | None = Field(default=None, max_length=512)
    published_year: int | None = None
    pages_count: int | None = None
    isbn: str | None = None
    cover_url: str | None = None
    is_primary: bool | None = None

class GetEdition(BaseModel):
    """Edition data returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    work_id: int
    work_title: str | None = None
    title: str
    language: str
    publisher: str | None
    published_year: int | None
    pages_count: int | None
    isbn: str | None
    cover_url: str | None
    google_books_id: str
    open_library_id: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime
