from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

class LibrarianSubmissionStatus(str, Enum):
    """Lifecycle states of a librarian submission."""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class CreateLibrarianSubmission(BaseModel):
    """Request payload for submitting a new book proposal for librarian review."""

    title: str = Field(max_length=512)
    language: str = Field(max_length=100)
    author_name: str = Field(max_length=512)
    isbn: str | None = Field(max_length=20)
    cover_url: str | None = None

class SetLibrarianSubmissionWork(BaseModel):
    """Request payload for linking an approved submission to its resulting catalog Work."""

    resulting_work_id: int

class GetLibrarianSubmission(BaseModel):
    """Librarian submission data returned in API responses."""

    id: int
    submitted_by_id: int
    submitted_by_username: str | None = None
    title: str
    language: str
    author_name: str
    isbn: str | None
    cover_url: str | None
    status: str
    reviewed_by_id: int | None
    reviewed_by_username: str | None = None
    reviewed_at: datetime | None
    resulting_work_id: int | None
    resulting_work_title: str | None = None
    created_at: datetime
