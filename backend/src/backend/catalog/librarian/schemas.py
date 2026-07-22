from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

class LibrarianSubmissionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class CreateLibrarianSubmission(BaseModel):
    title: str = Field(max_length=512)
    language: str = Field(max_length=100)
    author_name: str = Field(max_length=512)
    isbn: str | None = Field(max_length=20)
    cover_url: str | None = None

class SetLibrarianSubmissionWork(BaseModel):
    resulting_work_id: int

class GetLibrarianSubmission(BaseModel):
    id: int
    submitted_by_id: int
    title: str
    language: str
    author_name: str
    isbn: str | None
    cover_url: str | None
    status: str
    reviewed_by_id: int | None
    reviewed_at: datetime | None
    resulting_work_id: int | None
    created_at: datetime
