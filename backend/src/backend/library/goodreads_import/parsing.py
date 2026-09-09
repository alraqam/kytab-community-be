import csv
import io
from dataclasses import dataclass
from datetime import date, datetime

from src.backend.library.goodreads_import.exceptions import InvalidGoodreadsFileError
from src.backend.library.shelf.schemas import ShelfDefault

REQUIRED_COLUMNS = {"Title", "Author", "Exclusive Shelf"}
GOODREADS_DATE_FORMAT = "%Y/%m/%d"
DNF_SHELF_NAMES = {"did-not-finish", "didnotfinish", "dnf", "abandoned"}
EXCLUSIVE_SHELF_MAP = {
    "to-read": ShelfDefault.want_to_read,
    "currently-reading": ShelfDefault.currently_reading,
    "read": ShelfDefault.read,
}


@dataclass
class GoodreadsCsvRow:
    """A single parsed row from a Goodreads CSV export."""

    title: str
    author: str
    isbn: str | None
    isbn13: str | None
    rating: float | None
    review: str | None
    status: str
    date_added: date | None
    date_read: date | None


def _clean_isbn(raw: str | None) -> str | None:
    """Strips Goodreads' `="..."` spreadsheet-formula wrapping off an ISBN cell."""
    if not raw:
        return None
    value = raw.strip().lstrip("=").strip('"').strip()
    return value or None


def _parse_date(raw: str | None) -> date | None:
    """Parses a Goodreads YYYY/MM/DD date cell, returning None if blank or malformed."""
    if not raw or not raw.strip():
        return None
    try:
        return datetime.strptime(raw.strip(), GOODREADS_DATE_FORMAT).date()
    except ValueError:
        return None


def _parse_rating(raw: str | None) -> float | None:
    """Parses a Goodreads My Rating cell; 0 (and anything unparsable) means unrated."""
    if not raw or not raw.strip():
        return None
    try:
        value = float(raw.strip())
    except ValueError:
        return None
    return value if value > 0 else None


def _resolve_status(exclusive_shelf: str, bookshelves: str) -> str:
    """Maps Goodreads' Exclusive Shelf to a default status, with DNF detected from Bookshelves.

    Goodreads has no native "did not finish" exclusive shelf, so DNF is only
    ever expressed as a custom bookshelf name; we recognize the common
    spellings and let that override the exclusive shelf mapping.
    """
    shelf_names = {name.strip().lower().replace(" ", "-") for name in bookshelves.split(",") if name.strip()}
    if shelf_names & DNF_SHELF_NAMES:
        return ShelfDefault.did_not_finish
    return EXCLUSIVE_SHELF_MAP.get(exclusive_shelf.strip().lower(), ShelfDefault.want_to_read)


def parse_goodreads_csv(content: bytes) -> list[GoodreadsCsvRow]:
    """Parses the bytes of a Goodreads CSV export into structured rows.

    Args:
        content: Raw bytes of the uploaded CSV file.

    Returns:
        List of parsed GoodreadsCsvRow entries; rows missing a title or author are skipped.

    Raises:
        InvalidGoodreadsFileError: When the file is not UTF-8 text or is missing the
            columns a Goodreads export always has.
    """
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InvalidGoodreadsFileError("File is not valid UTF-8 text") from exc

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        raise InvalidGoodreadsFileError("File does not look like a Goodreads export")

    rows = []
    for raw_row in reader:
        title = (raw_row.get("Title") or "").strip()
        author = (raw_row.get("Author") or "").strip()
        if not title or not author:
            continue

        rows.append(
            GoodreadsCsvRow(
                title=title,
                author=author,
                isbn=_clean_isbn(raw_row.get("ISBN")),
                isbn13=_clean_isbn(raw_row.get("ISBN13")),
                rating=_parse_rating(raw_row.get("My Rating")),
                review=(raw_row.get("My Review") or "").strip() or None,
                status=_resolve_status(raw_row.get("Exclusive Shelf") or "", raw_row.get("Bookshelves") or ""),
                date_added=_parse_date(raw_row.get("Date Added")),
                date_read=_parse_date(raw_row.get("Date Read")),
            )
        )
    return rows
