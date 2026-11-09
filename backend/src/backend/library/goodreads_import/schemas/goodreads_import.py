from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class GoodreadsImportRowStatus(str, Enum):
    """Lifecycle states of a Goodreads import row."""

    unmatched = "unmatched"
    submitted = "submitted"

class GetGoodreadsImportRow(BaseModel):
    """Response payload representing an unmatched Goodreads import row."""

    id: int
    title: str
    author_name: str
    isbn: str | None
    status: str
    submission_id: int | None
    created_at: datetime

class GoodreadsImportReport(BaseModel):
    """Response payload summarizing the outcome of a Goodreads CSV import."""

    total_rows: int
    imported_count: int
    skipped_count: int
    unmatched: list[GetGoodreadsImportRow]
