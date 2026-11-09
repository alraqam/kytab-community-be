from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.library.goodreads_import.dependencies.goodreads_import import get_goodreads_import_manager, \
    get_goodreads_import_row_or_404
from src.backend.library.goodreads_import.managers.goodreads_import import GoodreadsImportManager
from src.backend.library.goodreads_import.models.goodreads_import import GoodreadsImportRow
from src.backend.library.goodreads_import.schemas.goodreads_import import GetGoodreadsImportRow, GoodreadsImportReport
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/library/goodreads-import",
    tags=["goodreads_import"],
)

@cbv(router)
class GoodreadsImportRouter:
    """CBV router for importing a Goodreads CSV export and resolving unmatched rows."""

    manager: GoodreadsImportManager = Depends(get_goodreads_import_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="importing a goodreads csv export",
        response_model=GoodreadsImportReport,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(400, 401, 403, 404, 409),
    )
    async def import_csv(
            self,
            file: UploadFile = File(...),
    ):
        """Imports a Goodreads CSV export into the current user's library."""
        result = await self.manager.import_csv(self.user, file)
        return result

    @router.get(
        "/rows",
        summary="getting current user's import rows",
        response_model=list[GetGoodreadsImportRow],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_my_rows(
            self,
    ):
        """Lists the current user's Goodreads import rows."""
        result = await self.manager.get_my_rows(self.user)
        return result

    @router.post(
        "/rows/{row_id}/submit",
        summary="submitting an unmatched row to the catalog queue",
        response_model=GetGoodreadsImportRow,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404, 409),
    )
    async def submit_row(
            self,
            row: GoodreadsImportRow = Depends(get_goodreads_import_row_or_404),
    ):
        """Submits an unmatched import row to the librarian catalog queue."""
        result = await self.manager.submit_row(self.user, row)
        return result
