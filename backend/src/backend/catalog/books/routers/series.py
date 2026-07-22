from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.series import get_series_manager, get_series_or_404
from src.backend.catalog.books.filters import SeriesFilter
from src.backend.catalog.books.managers.series import SeriesManager
from src.backend.catalog.books.models import Series
from src.backend.catalog.books.schemas.series import GetSeries
from src.backend.catalog.books.schemas.work import GetWork

router = APIRouter(
    prefix="/series",
    tags=["series"]
)


@cbv(router)
class SeriesRouter:
    """CBV router exposing Series read endpoints under /series."""

    manager: SeriesManager = Depends(get_series_manager)

    @router.get(
        "/",
        summary="getting all series",
        response_model=list[GetSeries],
    )
    async def get_all_series(
            self,
            filters: SeriesFilter = FilterDepends(SeriesFilter),
    ):
        """Returns all series with optional search and sort.

        Args:
            filters: SeriesFilter with optional search query and sort order.

        Returns:
            List of Series instances.
        """
        return await self.manager.get_all_series(filters)

    @router.get(
        "/{series_id}",
        summary="getting series by id",
        response_model=GetSeries,
    )
    async def get_series_by_id(
            self,
            series: Series = Depends(get_series_or_404),
    ):
        """Returns the series with the given ID.

        Args:
            series: Series instance resolved via get_series_or_404.

        Returns:
            Series instance.
        """
        return series

    @router.get(
        "/{series_id}/works",
        summary="getting works in series",
        response_model=list[GetWork],
    )
    async def get_works_for_series(
            self,
            series: Series = Depends(get_series_or_404),
    ):
        """Returns all works in the given series, in reading order.

        Args:
            series: Series instance resolved via get_series_or_404.

        Returns:
            List of Work instances.
        """
        return await self.manager.get_works_for_series(series.id)
