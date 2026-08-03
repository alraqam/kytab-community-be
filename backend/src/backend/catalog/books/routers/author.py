from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.author import get_author_manager, get_author_or_404
from src.backend.catalog.books.filters import AuthorFilter
from src.backend.catalog.books.managers.author import AuthorManager
from src.backend.catalog.books.models import Author
from src.backend.catalog.books.schemas.author import GetAuthor
from src.backend.catalog.books.schemas.work import GetWork

router = APIRouter(
    prefix="/authors",
    tags=["authors"]
)


@cbv(router)
class AuthorRouter:
    """CBV router exposing Author read endpoints under /authors."""

    manager: AuthorManager = Depends(get_author_manager)

    @router.get(
        "/",
        summary="getting all authors",
        response_model=list[GetAuthor],
    )
    async def get_authors(
            self,
            filters: AuthorFilter = FilterDepends(AuthorFilter),
    ):
        """Returns all authors with optional search and sort."""
        return await self.manager.get_all_authors(filters)

    @router.get(
        "/{author_id}",
        summary="getting author by id",
        response_model=GetAuthor,
    )
    async def get_author_by_id(
            self,
            author: Author = Depends(get_author_or_404),
    ):
        """Returns the author with the given ID."""
        return author

    @router.get(
        "/{author_id}/works",
        summary="getting works for author",
        response_model=list[GetWork],
    )
    async def get_works_for_author(
            self,
            author: Author = Depends(get_author_or_404),
    ):
        """Returns all works linked to the given author."""
        return await self.manager.get_works_for_author(author.id)
