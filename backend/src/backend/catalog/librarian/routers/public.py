from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.catalog.librarian.dependencies.librarian import get_librarian_submission_manager
from src.backend.catalog.librarian.managers.librarian import LibrarianSubmissionManager
from src.backend.catalog.librarian.schemas.librarian import GetLibrarianSubmission, CreateLibrarianSubmission
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/submission",
    tags=["submission"]
)

@cbv(router)
class LibrarianSubmissionPublicRouter:
    """CBV router allowing any authenticated user to submit a book proposal for librarian review."""

    manager: LibrarianSubmissionManager = Depends(get_librarian_submission_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating librarian submission",
        response_model=GetLibrarianSubmission,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404, 409),
    )
    async def create_submission(
            self,
            request: CreateLibrarianSubmission
    ):
        """Submits a new book proposal for librarian review."""
        result = await self.manager.create(self.user, request)
        return result