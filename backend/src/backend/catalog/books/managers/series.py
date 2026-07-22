from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.exceptions import SeriesNotFoundError, WorkNotFoundError, SeriesWorkLinkExistsError
from src.backend.catalog.books.filters import SeriesFilter
from src.backend.catalog.books.models import Series, Work
from src.backend.catalog.books.repository.series import SeriesRepository
from src.backend.catalog.books.repository.work import WorkRepository
from src.backend.catalog.books.schemas.series import CreateSeries, UpdateSeries, AddWorkToSeries


class SeriesManager:
    """Handles business logic for Series operations."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.series_repo = SeriesRepository(session)
        self.work_repo = WorkRepository(session)

    async def create_series(
            self,
            request: CreateSeries,
    ) -> Series:
        """Creates a new series.

        Args:
            request: CreateSeries payload with the series name.

        Returns:
            Newly created Series instance.
        """
        series = await self.series_repo.create_series(name=request.name)
        await self.session.commit()
        return series

    async def update_series(
            self,
            series_id: int,
            request: UpdateSeries,
    ) -> Series:
        """Updates an existing series.

        Args:
            series_id: ID of the series to update.
            request: UpdateSeries payload with the optional new name.

        Returns:
            Updated Series instance.

        Raises:
            SeriesNotFoundError: When no series with the given ID exists.
        """
        series = await self.get_series_by_id(series_id)
        await self.series_repo.update_series(series, name=request.name)
        await self.session.commit()
        return series

    async def delete_series(
            self,
            series_id: int,
    ) -> None:
        """Deletes a series.

        Args:
            series_id: ID of the series to delete.

        Raises:
            SeriesNotFoundError: When no series with the given ID exists.
        """
        series = await self.get_series_by_id(series_id)
        await self.series_repo.delete_series(series)
        await self.session.commit()

    async def get_series_by_id(
            self,
            series_id: int,
    ) -> Series:
        """Fetches a series by ID, raising an error if not found.

        Args:
            series_id: ID of the series to retrieve.

        Returns:
            Series instance.

        Raises:
            SeriesNotFoundError: When no series with the given ID exists.
        """
        series = await self.series_repo.get_series_by_id(series_id)
        if not series:
            raise SeriesNotFoundError("Series not found")
        return series

    async def get_all_series(
            self,
            filters: SeriesFilter | None = None,
    ) -> list[Series]:
        """Returns all series, optionally filtered and sorted.

        Args:
            filters: Optional SeriesFilter for searching (name) and sorting.

        Returns:
            List of Series instances.
        """
        return await self.series_repo.get_all_series(filters)

    async def add_work_to_series(
            self,
            request: AddWorkToSeries,
    ) -> None:
        """Links a work to a series.

        Args:
            request: AddWorkToSeries payload with work ID, series ID, and sequence number.

        Raises:
            WorkNotFoundError: When no work with the given ID exists.
            SeriesNotFoundError: When no series with the given ID exists.
        """
        work = await self.work_repo.get_work_by_id(request.work_id)
        if not work:
            raise WorkNotFoundError("Work not found")
        await self.get_series_by_id(request.series_id)

        try:
            await self.series_repo.add_work_to_series(
                request.work_id, request.series_id, request.sequence_number
            )
            await self.session.commit()
        except IntegrityError:
            raise SeriesWorkLinkExistsError("Series work link already exists")

    async def remove_work_from_series(
            self,
            work_id: int,
            series_id: int,
    ) -> None:
        """Removes a work-series link.

        Args:
            work_id: ID of the work.
            series_id: ID of the series.
        """
        link = await self.series_repo.get_work_series_link(work_id, series_id)
        if link:
            await self.series_repo.remove_work_from_series(link)
            await self.session.commit()

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
        return await self.series_repo.get_series_for_work(work_id)

    async def get_works_for_series(
            self,
            series_id: int,
    ) -> list[Work]:
        """Returns all works in a series, in reading order.

        Args:
            series_id: ID of the series.

        Returns:
            List of Work instances.
        """
        return await self.series_repo.get_works_for_series(series_id)
