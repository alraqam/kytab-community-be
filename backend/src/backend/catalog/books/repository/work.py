from dataclasses import dataclass

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.filters import WorkFilter
from src.backend.catalog.books.models import Work, Edition, WorkAuthor, WorkGenre, WorkSeries
from src.backend.clubs.reading_session.models import ReadingSession
from src.backend.library.reviews.models import Review
from src.backend.library.shelf.models import ShelfItem


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

    async def merge_works(
            self,
            source_id: int,
            target_id: int,
    ) -> None:
        """Reassigns everything referencing the source work to the target work.

        Drops rows that would collide with a unique constraint already
        satisfied on the target (e.g. the same shelf already holding the
        target work), then repoints the remaining rows.

        Args:
            source_id: ID of the duplicate work being merged away.
            target_id: ID of the canonical work absorbing the source.
        """
        conflicting_shelf_ids = select(ShelfItem.shelf_id).where(ShelfItem.work_id == target_id)
        await self.session.execute(
            delete(ShelfItem).where(
                and_(ShelfItem.work_id == source_id, ShelfItem.shelf_id.in_(conflicting_shelf_ids))
            )
        )
        await self.session.execute(
            update(ShelfItem).where(ShelfItem.work_id == source_id).values(work_id=target_id)
        )

        await self.session.execute(
            update(Edition).where(Edition.work_id == source_id).values(work_id=target_id)
        )
        await self.session.execute(
            update(Review).where(Review.work_id == source_id).values(work_id=target_id)
        )
        await self.session.execute(
            update(ReadingSession).where(ReadingSession.work_id == source_id).values(work_id=target_id)
        )

        conflicting_author_ids = select(WorkAuthor.author_id).where(WorkAuthor.work_id == target_id)
        await self.session.execute(
            delete(WorkAuthor).where(
                and_(WorkAuthor.work_id == source_id, WorkAuthor.author_id.in_(conflicting_author_ids))
            )
        )
        await self.session.execute(
            update(WorkAuthor).where(WorkAuthor.work_id == source_id).values(work_id=target_id)
        )

        conflicting_genre_ids = select(WorkGenre.genre_id).where(WorkGenre.work_id == target_id)
        await self.session.execute(
            delete(WorkGenre).where(
                and_(WorkGenre.work_id == source_id, WorkGenre.genre_id.in_(conflicting_genre_ids))
            )
        )
        await self.session.execute(
            update(WorkGenre).where(WorkGenre.work_id == source_id).values(work_id=target_id)
        )

        conflicting_series_ids = select(WorkSeries.series_id).where(WorkSeries.work_id == target_id)
        await self.session.execute(
            delete(WorkSeries).where(
                and_(WorkSeries.work_id == source_id, WorkSeries.series_id.in_(conflicting_series_ids))
            )
        )
        await self.session.execute(
            update(WorkSeries).where(WorkSeries.work_id == source_id).values(work_id=target_id)
        )

        await self.session.flush()
