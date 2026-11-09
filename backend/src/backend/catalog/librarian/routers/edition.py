from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models.auth import User
from src.backend.catalog.books.dependencies.edition import get_edition_manager, get_edition_or_404
from src.backend.catalog.books.managers.edition import EditionManager
from src.backend.catalog.books.models.book import Edition
from src.backend.catalog.books.schemas.edition import CreateEdition, UpdateEdition, GetEdition

from src.backend.catalog.librarian.dependencies.librarian import is_librarian
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/librarian/edition",
    tags=["librarian_edition"]
)


@cbv(router)
class LibrarianEditionRouter:
    """CBV router for librarian management of editions: create, update, and delete."""

    manager: EditionManager = Depends(get_edition_manager)
    user: User = Depends(is_librarian)

    @router.post(
        "/",
        summary="creating edition",
        response_model=GetEdition,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404),
    )
    async def create_edition(
            self,
            request: CreateEdition
    ):
        """Creates a new edition."""
        result = await self.manager.create_edition(request)
        return result

    @router.put(
        "/{edition_id}",
        summary="updating edition",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_edition(
            self,
            request: UpdateEdition,
            edition: Edition = Depends(get_edition_or_404)
    ):
        """Updates an existing edition's details."""
        await self.manager.update_edition(edition.id, request)

    @router.delete(
        "/{edition_id}",
        summary="deleting edition",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_edition(
            self,
            edition: Edition = Depends(get_edition_or_404)
    ):
        """Deletes an edition."""
        await self.manager.delete_edition(edition.id)

