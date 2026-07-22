from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.filters import WorkFilter
from src.backend.catalog.books.models import Work


@dataclass
class WorkRepository:
    """Data access layer for Work model operations."""

    session: AsyncSession

    async def create_work(
            self,
            canonical_title: str,
            description: str | None = None,
            primary_language: str | None = None,
    ) -> Work:
        """Creates and persists a new work record.

        Args:
            canonical_title: Title of the abstract work.
            description: Optional description text.
            primary_language: Optional primary language of the work.

        Returns:
            Newly created Work instance.
        """
        work = Work(
            canonical_title=canonical_title,
            description=description,
            primary_language=primary_language,
        )
        self.session.add(work)
        await self.session.flush()
        return work

    async def update_work(
            self,
            work: Work,
            canonical_title: str | None = None,
            description: str | None = None,
            primary_language: str | None = None,
    ) -> None:
        """Updates non-None fields on the work and flushes the session.

        Args:
            work: Work instance to update.
            canonical_title: New title, or None to leave unchanged.
            description: New description, or None to leave unchanged.
            primary_language: New primary language, or None to leave unchanged.
        """
        updates = {
            "canonical_title": canonical_title,
            "description": description,
            "primary_language": primary_language,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(work, field, value)
        await self.session.flush()

    async def delete_work(
            self,
            work: Work,
    ) -> None:
        """Deletes the work record and flushes the session.

        Args:
            work: Work instance to delete.
        """
        await self.session.delete(work)
        await self.session.flush()

    async def get_work_by_id(
            self,
            work_id: int,
    ) -> Work | None:
        """Fetches a work by its internal ID.

        Args:
            work_id: Internal database ID.

        Returns:
            Work instance if found, None otherwise.
        """
        stmt = select(Work).where(Work.id == work_id)
        result = await self.session.execute(stmt)
        work = result.scalar_one_or_none()
        return work

    async def get_all_works(
            self,
            filters: WorkFilter | None = None,
    ) -> list[Work]:
        """Returns all work records, optionally filtered and sorted.

        Args:
            filters: Optional WorkFilter for searching (title/description) and sorting.

        Returns:
            List of Work instances.
        """
        stmt = select(Work)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        works = list(result.scalars().all())
        return works
