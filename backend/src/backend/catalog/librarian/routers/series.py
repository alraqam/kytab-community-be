from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models.auth import User
from src.backend.catalog.books.dependencies.series import get_series_manager, get_series_or_404
from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.catalog.books.managers.series import SeriesManager
from src.backend.catalog.books.models.book import Work, Series
from src.backend.catalog.books.schemas.series import AddWorkToSeries, GetSeries, CreateSeries, UpdateSeries

from src.backend.catalog.librarian.dependencies.librarian import is_librarian
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/librarian/series",
    tags=["librarian_series"]
)

@cbv(router)
class LibrarianSeriesRouter:
    """CBV router for librarian management of series: create, update, delete, and link/unlink to works."""

    manager: SeriesManager = Depends(get_series_manager)
    user: User = Depends(is_librarian)

    @router.post(
        "/",
        summary="creating series",
        response_model=GetSeries,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403),
    )
    async def create_series(
            self,
            request: CreateSeries
    ):
        """Creates a new series."""
        result = await self.manager.create_series(request)
        return result

    @router.put(
        "/{series_id}",
        summary="updating series",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_series(
            self,
            request: UpdateSeries,
            series: Series = Depends(get_series_or_404)
    ):
        """Updates an existing series' details."""
        await self.manager.update_series(series.id, request)

    @router.delete(
        "/{series_id}",
        summary="deleting series",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_series(
            self,
            series: Series = Depends(get_series_or_404)
    ):
        """Deletes a series."""
        await self.manager.delete_series(series.id)

    @router.put(
        "/{series_id}/work/add",
        summary="adding series to work",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def add_series_to_work(
            self,
            request: AddWorkToSeries,
    ):
        """Links a work to a series."""
        await self.manager.add_work_to_series(request)

    @router.put(
        "/{series_id}/work/{work_id}/remove",
        summary="removing series from work",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def remove_series_from_work(
            self,
            series: Series = Depends(get_series_or_404),
            work: Work = Depends(get_work_or_404)
    ):
        """Removes the link between a work and a series."""
        await self.manager.remove_work_from_series(work.id, series.id)


