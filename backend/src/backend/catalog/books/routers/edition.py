from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.edition import get_edition_manager, get_edition_or_404
from src.backend.catalog.books.filters import EditionFilter
from src.backend.catalog.books.managers.edition import EditionManager
from src.backend.catalog.books.models import Edition
from src.backend.catalog.books.schemas.edition import GetEdition

router = APIRouter(
    prefix="/editions",
    tags=["editions"]
)


@cbv(router)
class EditionRouter:
    """CBV router exposing Edition read endpoints under /editions."""

    manager: EditionManager = Depends(get_edition_manager)

    @router.get(
        "/",
        summary="getting all editions",
        response_model=list[GetEdition],
    )
    async def get_editions(
            self,
            filters: EditionFilter = FilterDepends(EditionFilter),
    ):
        """Returns all editions with optional filtering and sort.

        Args:
            filters: EditionFilter with optional work_id, language, search query, and sort order.

        Returns:
            List of Edition instances.
        """
        return await self.manager.get_all_editions(filters)

    @router.get(
        "/{edition_id}",
        summary="getting edition by id",
        response_model=GetEdition,
    )
    async def get_edition_by_id(
            self,
            edition: Edition = Depends(get_edition_or_404),
    ):
        """Returns the edition with the given ID.

        Args:
            edition: Edition instance resolved via get_edition_or_404.

        Returns:
            Edition instance.
        """
        return edition
