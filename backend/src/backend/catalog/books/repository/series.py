from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.filters import SeriesFilter
from src.backend.catalog.books.models import Series, WorkSeries, Work


@dataclass
class SeriesRepository:
    """Data access layer for Series model operations."""

    session: AsyncSession

    async def create_series(
            self,
            name: str,
    ) -> Series:
        """Creates and persists a new series record.

        Args:
            name: Series name.

        Returns:
            Newly created Series instance.
        """
        series = Series(name=name)
        self.session.add(series)
        await self.session.flush()
        return series

    async def update_series(
            self,
            series: Series,
            name: str | None = None,
    ) -> None:
        """Updates non-None fields on the series and flushes the session.

        Args:
            series: Series instance to update.
            name: New name, or None to leave unchanged.
        """
        if name is not None:
            series.name = name
        await self.session.flush()

    async def delete_series(
            self,
            series: Series,
    ) -> None:
        """Deletes the series record and flushes the session.

        Args:
            series: Series instance to delete.
        """
        await self.session.delete(series)
        await self.session.flush()

    async def get_series_by_id(
            self,
            series_id: int,
    ) -> Series | None:
        """Fetches a series by its internal ID.

        Args:
            series_id: Internal database ID.

        Returns:
            Series instance if found, None otherwise.
        """
        stmt = select(Series).where(Series.id == series_id)
        result = await self.session.execute(stmt)
        series = result.scalar_one_or_none()
        return series

    async def get_all_series(
            self,
            filters: SeriesFilter | None = None,
    ) -> list[Series]:
        """Returns all series records, optionally filtered and sorted.

        Args:
            filters: Optional SeriesFilter for searching (name) and sorting.

        Returns:
            List of Series instances.
        """
        stmt = select(Series)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        series = list(result.scalars().all())
        return series

    async def add_work_to_series(
            self,
            work_id: int,
            series_id: int,
            sequence_number: int | None = None,
    ) -> WorkSeries:
        """Links a work to a series.

        Args:
            work_id: ID of the work.
            series_id: ID of the series.
            sequence_number: Optional position of the work within the series.

        Returns:
            Newly created WorkSeries link instance.
        """
        link = WorkSeries(
            work_id=work_id,
            series_id=series_id,
            sequence_number=sequence_number,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_work_series_link(
            self,
            work_id: int,
            series_id: int,
    ) -> WorkSeries | None:
        """Fetches the link record between a work and a series.

        Args:
            work_id: ID of the work.
            series_id: ID of the series.

        Returns:
            WorkSeries instance if found, None otherwise.
        """
        stmt = select(WorkSeries).where(
            and_(
                WorkSeries.work_id == work_id,
                WorkSeries.series_id == series_id,
            )
        )
        result = await self.session.execute(stmt)
        work = result.scalar_one_or_none()
        return work

    async def remove_work_from_series(
            self,
            link: WorkSeries,
    ) -> None:
        """Removes a work-series link and flushes the session.

        Args:
            link: WorkSeries instance to delete.
        """
        await self.session.delete(link)
        await self.session.flush()

    async def get_series_for_work(
            self,
            work_id: int,
    ) -> list[Series]:
        """Returns all series a work belongs to.

        Args:
            work_id: ID of the work.

        Returns:
            List of Series instances.
        """
        stmt = (
            select(Series)
            .join(WorkSeries, WorkSeries.series_id == Series.id)
            .where(WorkSeries.work_id == work_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_works_for_series(
            self,
            series_id: int,
    ) -> list[Work]:
        """Returns all works in a series, ordered by sequence number.

        Args:
            series_id: ID of the series.

        Returns:
            List of Work instances in reading order.
        """
        stmt = (
            select(Work)
            .join(WorkSeries, WorkSeries.work_id == Work.id)
            .where(WorkSeries.series_id == series_id)
            .order_by(WorkSeries.sequence_number)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
