from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.genre import get_genre_manager, get_genre_or_404
from src.backend.catalog.books.filters import GenreFilter
from src.backend.catalog.books.managers.genre import GenreManager
from src.backend.catalog.books.models import Genre
from src.backend.catalog.books.schemas.genre import GetGenre
from src.backend.catalog.books.schemas.work import GetWork

router = APIRouter(
    prefix="/genres",
    tags=["genres"]
)


@cbv(router)
class GenreRouter:
    """CBV router exposing Genre read endpoints under /genres."""

    manager: GenreManager = Depends(get_genre_manager)

    @router.get(
        "/",
        summary="getting all genres",
        response_model=list[GetGenre],
    )
    async def get_genres(
            self,
            filters: GenreFilter = FilterDepends(GenreFilter),
    ):
        """Returns all genres with optional search and sort.

        Args:
            filters: GenreFilter with optional search query and sort order.

        Returns:
            List of Genre instances.
        """
        return await self.manager.get_all_genres(filters)

    @router.get(
        "/{genre_id}",
        summary="getting genre by id",
        response_model=GetGenre,
    )
    async def get_genre_by_id(
            self,
            genre: Genre = Depends(get_genre_or_404),
    ):
        """Returns the genre with the given ID.

        Args:
            genre: Genre instance resolved via get_genre_or_404.

        Returns:
            Genre instance.
        """
        return genre

    @router.get(
        "/{genre_id}/works",
        summary="getting works tagged with genre",
        response_model=list[GetWork],
    )
    async def get_works_for_genre(
            self,
            genre: Genre = Depends(get_genre_or_404),
    ):
        """Returns all works tagged with the given genre.

        Args:
            genre: Genre instance resolved via get_genre_or_404.

        Returns:
            List of Work instances.
        """
        return await self.manager.get_works_for_genre(genre.id)
