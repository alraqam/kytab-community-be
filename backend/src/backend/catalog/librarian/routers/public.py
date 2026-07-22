from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.catalog.librarian.dependencies import get_librarian_submission_manager
from src.backend.catalog.librarian.managers import LibrarianSubmissionManager
from src.backend.catalog.librarian.schemas import GetLibrarianSubmission, CreateLibrarianSubmission

router = APIRouter(
    prefix="/submission",
    tags=["submission"]
)

@cbv(router)
class LibrarianSubmissionPublicRouter:
    manager: LibrarianSubmissionManager = Depends(get_librarian_submission_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating librarian submission",
        response_model=GetLibrarianSubmission,
    )
    async def create_submission(
            self,
            request: CreateLibrarianSubmission
    ):
        result = await self.manager.create(self.user, request)
        return result