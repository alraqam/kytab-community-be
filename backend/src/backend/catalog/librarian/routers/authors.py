from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models.auth import User
from src.backend.catalog.books.dependencies.author import get_author_manager, get_author_or_404
from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.catalog.books.managers.author import AuthorManager
from src.backend.catalog.books.models.book import Author, Work
from src.backend.catalog.books.schemas.author import CreateAuthor, UpdateAuthor, AddAuthorToWork, GetAuthor
from src.backend.catalog.librarian.dependencies.librarian import is_librarian
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/librarian/author",
    tags=["librarian_author"]
)

@cbv(router)
class LibrarianAuthorRouter:
    """CBV router for librarian management of authors: create, update, delete, and link/unlink to works."""

    manager: AuthorManager = Depends(get_author_manager)
    user: User = Depends(is_librarian)

    @router.post(
        "/",
        summary="creating author",
        response_model=GetAuthor,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403),
    )
    async def create_author(
            self,
            request: CreateAuthor
    ):
        """Creates a new author."""
        result = await self.manager.create_author(request)
        return result

    @router.put(
        "/{author_id}",
        summary="updating author",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_author(
            self,
            request: UpdateAuthor,
            author: Author = Depends(get_author_or_404)
    ):
        """Updates an existing author's details."""
        await self.manager.update_author(author.id, request)

    @router.delete(
        "/{author_id}",
        summary="deleting author",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_author(
            self,
            author: Author = Depends(get_author_or_404)
    ):
        """Deletes an author."""
        await self.manager.delete_author(author.id)

    @router.put(
        "/{author_id}/work/add",
        summary="adding author to work",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def add_author_to_work(
            self,
            request: AddAuthorToWork,
    ):
        """Links an author to a work."""
        await self.manager.add_author_to_work(request)

    @router.put(
        "/{author_id}/work/{work_id}/remove",
        summary="removing author from work",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def remove_author_from_work(
            self,
            author: Author = Depends(get_author_or_404),
            work: Work = Depends(get_work_or_404)
    ):
        """Removes the link between an author and a work."""
        await self.manager.remove_author_from_work(work.id, author.id)


