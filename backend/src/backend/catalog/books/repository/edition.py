from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.filters import EditionFilter
from src.backend.catalog.books.models import Edition


@dataclass
class EditionRepository:
    """Data access layer for Edition model operations."""

    session: AsyncSession

    async def create_edition(
            self,
            work_id: int,
            title: str,
            language: str,
            google_books_id: str,
            open_library_id: str,
            publisher: str | None = None,
            published_year: int | None = None,
            pages_count: int | None = None,
            isbn: int | None = None,
            cover_url: str | None = None,
            is_primary: bool = False,
    ) -> Edition:
        """Creates and persists a new edition record.

        Args:
            work_id: ID of the parent Work.
            title: Edition-specific title.
            language: Language of this edition.
            google_books_id: Google Books volume ID.
            open_library_id: Open Library ID.
            publisher: Optional publisher name.
            published_year: Optional year of publication.
            pages_count: Optional page count.
            isbn: Optional ISBN.
            cover_url: Optional cover image URL.
            is_primary: Whether this is the primary edition for the work.

        Returns:
            Newly created Edition instance.
        """
        edition = Edition(
            work_id=work_id,
            title=title,
            language=language,
            google_books_id=google_books_id,
            open_library_id=open_library_id,
            publisher=publisher,
            published_year=published_year,
            pages_count=pages_count,
            isbn=isbn,
            cover_url=cover_url,
            is_primary=is_primary,
        )
        self.session.add(edition)
        await self.session.flush()
        return edition

    async def update_edition(
            self,
            edition: Edition,
            title: str | None = None,
            language: str | None = None,
            publisher: str | None = None,
            published_year: int | None = None,
            pages_count: int | None = None,
            isbn: int | None = None,
            cover_url: str | None = None,
            is_primary: bool | None = None,
    ) -> None:
        """Updates non-None fields on the edition and flushes the session.

        Args:
            edition: Edition instance to update.
            title: New title, or None to leave unchanged.
            language: New language, or None to leave unchanged.
            publisher: New publisher, or None to leave unchanged.
            published_year: New publication year, or None to leave unchanged.
            pages_count: New page count, or None to leave unchanged.
            isbn: New ISBN, or None to leave unchanged.
            cover_url: New cover URL, or None to leave unchanged.
            is_primary: New primary flag, or None to leave unchanged.
        """
        updates = {
            "title": title,
            "language": language,
            "publisher": publisher,
            "published_year": published_year,
            "pages_count": pages_count,
            "isbn": isbn,
            "cover_url": cover_url,
            "is_primary": is_primary,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(edition, field, value)
        await self.session.flush()

    async def delete_edition(
            self,
            edition: Edition,
    ) -> None:
        """Deletes the edition record and flushes the session.

        Args:
            edition: Edition instance to delete.
        """
        await self.session.delete(edition)
        await self.session.flush()

    async def get_edition_by_id(
            self,
            edition_id: int,
    ) -> Edition | None:
        """Fetches an edition by its internal ID.

        Args:
            edition_id: Internal database ID.

        Returns:
            Edition instance if found, None otherwise.
        """
        stmt = select(Edition).where(Edition.id == edition_id)
        result = await self.session.execute(stmt)
        edition =  result.scalar_one_or_none()
        return edition

    async def get_edition_by_google_id(
            self,
            google_books_id: str,
    ) -> Edition | None:
        """Fetches an edition by its Google Books ID.

        Args:
            google_books_id: Google Books volume ID string.

        Returns:
            Edition instance if found, None otherwise.
        """
        stmt = select(Edition).where(Edition.google_books_id == google_books_id)
        result = await self.session.execute(stmt)
        edition =  result.scalar_one_or_none()
        return edition

    async def get_edition_by_open_library_id(
            self,
            open_library_id: str,
    ) -> Edition | None:
        """Fetches an edition by its Open Library ID.

        Args:
            open_library_id: Open Library ID string.

        Returns:
            Edition instance if found, None otherwise.
        """
        stmt = select(Edition).where(Edition.open_library_id == open_library_id)
        result = await self.session.execute(stmt)
        edition = result.scalar_one_or_none()
        return edition

    async def get_editions_by_work(
            self,
            work_id: int,
    ) -> list[Edition]:
        """Returns all editions belonging to a work.

        Args:
            work_id: ID of the parent Work.

        Returns:
            List of Edition instances.
        """
        stmt = select(Edition).where(Edition.work_id == work_id)
        result = await self.session.execute(stmt)
        editions =  list(result.scalars().all())
        return editions

    async def get_all_editions(
            self,
            filters: EditionFilter | None = None,
    ) -> list[Edition]:
        """Returns all edition records, optionally filtered and sorted.

        Args:
            filters: Optional EditionFilter for filtering (work_id/language/title/isbn) and sorting.

        Returns:
            List of Edition instances.
        """
        stmt = select(Edition)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        editions = list(result.scalars().all())
        return editions