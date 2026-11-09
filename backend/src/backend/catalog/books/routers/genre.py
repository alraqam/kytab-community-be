from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.genre import get_genre_manager, get_genre_or_404
from src.backend.catalog.books.filters.book import GenreFilter
from src.backend.catalog.books.managers.genre import GenreManager
from src.backend.catalog.books.models.book import Genre
from src.backend.catalog.books.schemas.genre import GetGenre
from src.backend.catalog.books.schemas.work import GetWork
from src.backend.core.responses import error_responses

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
        status_code=status.HTTP_200_OK,
    )
    async def get_genres(
            self,
            filters: GenreFilter = FilterDepends(GenreFilter),
    ):
        """Returns all genres with optional search and sort."""
        return await self.manager.get_all_genres(filters)

    @router.get(
        "/{genre_id}",
        summary="getting genre by id",
        response_model=GetGenre,
        status_code=status.HTTP_200_OK,
        responses=error_responses(404),
    )
    async def get_genre_by_id(
            self,
            genre: Genre = Depends(get_genre_or_404),
    ):
        """Returns the genre with the given ID."""
        return genre

    @router.get(
        "/{genre_id}/works",
        summary="getting works tagged with genre",
        response_model=list[GetWork],
        status_code=status.HTTP_200_OK,
        responses=error_responses(404),
    )
    async def get_works_for_genre(
            self,
            genre: Genre = Depends(get_genre_or_404),
    ):
        """Returns all works tagged with the given genre."""
        return await self.manager.get_works_for_genre(genre.id)
