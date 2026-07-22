from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models import User
from src.backend.catalog.books.dependencies.genre import get_genre_manager, get_genre_or_404
from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.catalog.books.managers.genre import GenreManager
from src.backend.catalog.books.models import Work, Genre
from src.backend.catalog.books.schemas.genre import AddGenreToWork, GetGenre, CreateGenre, UpdateGenre

from src.backend.catalog.librarian.dependencies import is_librarian

router = APIRouter(
    prefix="/librarian/genre",
    tags=["librarian_genre"]
)

@cbv(router)
class LibrarianGenreRouter:
    manager: GenreManager = Depends(get_genre_manager)
    user: User = Depends(is_librarian)

    @router.post(
        "/",
        summary="creating genre",
        response_model=GetGenre
    )
    async def create_genre(
            self,
            request: CreateGenre
    ):
        result = await self.manager.create_genre(request)
        return result

    @router.put(
        "/{genre_id}",
        summary="updating genre",
    )
    async def update_genre(
            self,
            request: UpdateGenre,
            genre: Genre = Depends(get_genre_or_404)
    ):
        await self.manager.update_genre(genre.id, request)

    @router.delete(
        "/{genre_id}",
        summary="deleting genre",
    )
    async def delete_genre(
            self,
            genre: Genre = Depends(get_genre_or_404)
    ):
        await self.manager.delete_genre(genre.id)

    @router.put(
        "/{genre_id}/work/add",
        summary="adding genre to work",
    )
    async def add_genre_to_work(
            self,
            request: AddGenreToWork,
    ):
        await self.manager.add_genre_to_work(request)

    @router.put(
        "/{genre_id}/work/{work_id}/remove",
        summary="removing genre from work",
    )
    async def remove_genre_from_work(
            self,
            genre: Genre = Depends(get_genre_or_404),
            work: Work = Depends(get_work_or_404)
    ):
        await self.manager.remove_genre_from_work(work.id, genre.id)


