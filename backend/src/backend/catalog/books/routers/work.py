from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.author import get_author_manager
from src.backend.catalog.books.dependencies.edition import get_edition_manager
from src.backend.catalog.books.dependencies.genre import get_genre_manager
from src.backend.catalog.books.dependencies.series import get_series_manager
from src.backend.catalog.books.dependencies.work import get_work_manager, get_work_or_404
from src.backend.catalog.books.filters import WorkFilter
from src.backend.catalog.books.managers.author import AuthorManager
from src.backend.catalog.books.managers.edition import EditionManager
from src.backend.catalog.books.managers.genre import GenreManager
from src.backend.catalog.books.managers.series import SeriesManager
from src.backend.catalog.books.managers.work import WorkManager
from src.backend.catalog.books.models import Work
from src.backend.catalog.books.schemas.author import GetAuthor
from src.backend.catalog.books.schemas.edition import GetEdition
from src.backend.catalog.books.schemas.genre import GetGenre
from src.backend.catalog.books.schemas.series import GetSeries
from src.backend.catalog.books.schemas.work import GetWork

router = APIRouter(
    prefix="/works",
    tags=["works"]
)


@cbv(router)
class WorkRouter:
    """CBV router exposing Work read endpoints under /works."""

    manager: WorkManager = Depends(get_work_manager)
    edition_manager: EditionManager = Depends(get_edition_manager)
    author_manager: AuthorManager = Depends(get_author_manager)
    genre_manager: GenreManager = Depends(get_genre_manager)
    series_manager: SeriesManager = Depends(get_series_manager)

    @router.get(
        "/",
        summary="getting all works",
        response_model=list[GetWork],
    )
    async def get_works(
            self,
            filters: WorkFilter = FilterDepends(WorkFilter),
    ):
        """Returns all works with optional search and sort."""
        return await self.manager.get_all_works(filters)

    @router.get(
        "/{work_id}",
        summary="getting work by id",
        response_model=GetWork,
    )
    async def get_work_by_id(
            self,
            work: Work = Depends(get_work_or_404),
    ):
        """Returns the work with the given ID."""
        return work

    @router.get(
        "/{work_id}/edition",
        summary="getting work's editions",
        response_model=list[GetEdition],
    )
    async def get_editions_by_work(
            self,
            work: Work = Depends(get_work_or_404),
    ):
        """Returns all editions linked to the given work."""
        return await self.edition_manager.get_editions_by_work(work.id)

    @router.get(
        "/{work_id}/authors",
        summary="getting work's authors",
        response_model=list[GetAuthor],
    )
    async def get_authors_for_work(
            self,
            work: Work = Depends(get_work_or_404),
    ):
        """Returns all author linked to the given work."""
        return await self.author_manager.get_authors_for_work(work.id)

    @router.get(
        "/{work_id}/genres",
        summary="getting work's genres",
        response_model=list[GetGenre],
    )
    async def get_genres_for_work(
            self,
            work: Work = Depends(get_work_or_404),
    ):
        """Returns all genre linked to the given work."""
        return await self.genre_manager.get_genres_for_work(work.id)

    @router.get(
        "/{work_id}/series",
        summary="getting work's series",
        response_model=list[GetSeries],
    )
    async def get_genres_for_work(
            self,
            work: Work = Depends(get_work_or_404),
    ):
        """Returns all series linked to the given work."""
        return await self.series_manager.get_series_for_work(work.id)
