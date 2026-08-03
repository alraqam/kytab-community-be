from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.models import Edition
from src.backend.library.progress.models import ReadingPeriod
from src.backend.library.shelf.models import Shelf, ShelfItem


@dataclass
class ReadingPeriodRepository:
    """Data-access layer for reading period persistence and queries."""

    session: AsyncSession

    async def start_reading_period(
            self,
            shelf_item_id: int,
    ) -> ReadingPeriod:
        """Inserts a new reading period starting now for a shelf item.

        Args:
            shelf_item_id: ID of the shelf item the reading period belongs to.

        Returns:
            Newly created ReadingPeriod instance.
        """
        result = ReadingPeriod(
            shelf_item_id=shelf_item_id,
            started_at=datetime.now(),
            finished_at=None,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def set_finishing_date(
            self,
            reading_period: ReadingPeriod,
    ) -> None:
        """Stamps a reading period as finished at the current time.

        Args:
            reading_period: ReadingPeriod instance to mark finished.
        """
        reading_period.finished_at = datetime.now()
        self.session.add(reading_period)
        await self.session.flush()

    async def delete_reading_period(
            self,
            reading_period: ReadingPeriod,
    ) -> None:
        """Deletes a reading period.

        Args:
            reading_period: ReadingPeriod instance to delete.
        """
        await self.session.delete(reading_period)
        await self.session.flush()

    async def get_user_reading_periods(
            self,
            user_id: int
    ) -> list[ReadingPeriod]:
        """Lists all reading periods across a user's shelves.

        Args:
            user_id: ID of the user whose reading periods are listed.

        Returns:
            List of matching ReadingPeriod instances.
        """
        stmt = (
            select(ReadingPeriod)
            .join(ShelfItem, ReadingPeriod.shelf_item_id == ShelfItem.id)
            .join(Shelf, ShelfItem.shelf_id == Shelf.id)
            .where(Shelf.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_shelf_item_periods(
            self,
            shelf_item: int
    ) -> list[ReadingPeriod]:
        """Lists all reading periods for a shelf item.

        Args:
            shelf_item: ID of the shelf item to list reading periods for.

        Returns:
            List of matching ReadingPeriod instances.
        """
        stmt = select(ReadingPeriod).where(ReadingPeriod.shelf_item_id == shelf_item)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_reading_period_by_id(
            self,
            reading_period_id: int
    ) -> ReadingPeriod | None:
        """Fetches a single reading period by ID.

        Args:
            reading_period_id: ID of the reading period to fetch.

        Returns:
            Matching ReadingPeriod instance, or None if not found.
        """
        stmt = select(ReadingPeriod).where(ReadingPeriod.id == reading_period_id)
        result = await self.session.execute(stmt)
        reading_period = result.scalar_one_or_none()
        return reading_period

    async def get_shelf_by_period(
            self,
            reading_period_id: int
    ) -> Shelf | None:
        """Fetches the shelf that owns a reading period, via its shelf item.

        Args:
            reading_period_id: ID of the reading period to look up.

        Returns:
            Matching Shelf instance, or None if not found.
        """
        stmt = (
            select(Shelf)
            .join(ShelfItem, ShelfItem.shelf_id == Shelf.id)
            .join(ReadingPeriod, ReadingPeriod.shelf_item_id == ShelfItem.id)
            .where(ReadingPeriod.id == reading_period_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_shelf_item_by_period(
            self,
            reading_period_id: int
    ) -> ShelfItem | None:
        """Fetches the shelf item associated with a reading period.

        Args:
            reading_period_id: ID of the reading period to look up.

        Returns:
            Matching ShelfItem instance, or None if not found.
        """
        stmt = (
            select(ShelfItem)
            .join(ReadingPeriod, ReadingPeriod.shelf_item_id == ShelfItem.id)
            .where(ReadingPeriod.id == reading_period_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_active_period(
            self,
            user_id: int,
            work_id: int
    ) -> Shelf | None:
        """Checks whether the user has an unfinished reading period for the given work.

        Args:
            user_id: ID of the user to check.
            work_id: ID of the work to check for an active reading period.

        Returns:
            The matching Shelf instance if an active period exists, otherwise None.
        """
        stmt = (
            select(Shelf)
            .join(ShelfItem, ShelfItem.shelf_id == Shelf.id)
            .join(ReadingPeriod, ReadingPeriod.shelf_item_id == ShelfItem.id)
            .where(
                and_(
                   Shelf.user_id == user_id,
                   ShelfItem.work_id == work_id,
                    ReadingPeriod.finished_at.is_(None),
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_edition_by_reading_period(
            self,
            reading_period_id: int
    ) -> Edition | None:
        """Fetches the edition associated with a reading period's shelf item.

        Args:
            reading_period_id: ID of the reading period to look up.

        Returns:
            Matching Edition instance, or None if not found.
        """
        stmt = (
            select(Edition)
            .join(ShelfItem, ShelfItem.edition_id == Edition.id)
            .join(ReadingPeriod, ReadingPeriod.shelf_item_id == ShelfItem.id)
            .where(ReadingPeriod.id == reading_period_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()