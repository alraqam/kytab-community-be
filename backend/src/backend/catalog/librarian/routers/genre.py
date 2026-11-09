from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models.auth import User
from src.backend.catalog.books.dependencies.genre import get_genre_manager, get_genre_or_404
from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.catalog.books.managers.genre import GenreManager
from src.backend.catalog.books.models.book import Work, Genre
from src.backend.catalog.books.schemas.genre import AddGenreToWork, GetGenre, CreateGenre, UpdateGenre

from src.backend.catalog.librarian.dependencies.librarian import is_librarian
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/librarian/genre",
    tags=["librarian_genre"]
)

@cbv(router)
class LibrarianGenreRouter:
    """CBV router for librarian management of genres: create, update, delete, and link/unlink to works."""

    manager: GenreManager = Depends(get_genre_manager)
    user: User = Depends(is_librarian)

    @router.post(
        "/",
        summary="creating genre",
        response_model=GetGenre,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403),
    )
    async def create_genre(
            self,
            request: CreateGenre
    ):
        """Creates a new genre."""
        result = await self.manager.create_genre(request)
        return result

    @router.put(
        "/{genre_id}",
        summary="updating genre",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_genre(
            self,
            request: UpdateGenre,
            genre: Genre = Depends(get_genre_or_404)
    ):
        """Updates an existing genre's details."""
        await self.manager.update_genre(genre.id, request)

    @router.delete(
        "/{genre_id}",
        summary="deleting genre",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_genre(
            self,
            genre: Genre = Depends(get_genre_or_404)
    ):
        """Deletes a genre."""
        await self.manager.delete_genre(genre.id)

    @router.put(
        "/{genre_id}/work/add",
        summary="adding genre to work",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def add_genre_to_work(
            self,
            request: AddGenreToWork,
    ):
        """Links a genre to a work."""
        await self.manager.add_genre_to_work(request)

    @router.put(
        "/{genre_id}/work/{work_id}/remove",
        summary="removing genre from work",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def remove_genre_from_work(
            self,
            genre: Genre = Depends(get_genre_or_404),
            work: Work = Depends(get_work_or_404)
    ):
        """Removes the link between a genre and a work."""
        await self.manager.remove_genre_from_work(work.id, genre.id)


