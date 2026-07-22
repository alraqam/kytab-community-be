from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models import User
from src.backend.catalog.librarian.dependencies import get_librarian_submission_manager, is_librarian, \
    get_librarian_submission_or_404
from src.backend.catalog.librarian.filters import LibrarianSubmissionFilter
from src.backend.catalog.librarian.managers import LibrarianSubmissionManager
from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.catalog.librarian.schemas import SetLibrarianSubmissionWork, GetLibrarianSubmission

router = APIRouter(
    prefix="/librarian/submission",
    tags=["librarian_submission"]
)

@cbv(router)
class LibrarianSubmissionRouter:
    manager: LibrarianSubmissionManager = Depends(get_librarian_submission_manager)
    user: User = Depends(is_librarian)

    @router.put(
        "/{submission_id}/approve",
        summary="approving submission",
    )
    async def approve(
            self,
            submission: LibrarianSubmission = Depends(get_librarian_submission_or_404)
    ):
        await self.manager.approve(self.user, submission)

    @router.put(
        "/{submission_id}/reject",
        summary="rejecting submission",
    )
    async def reject(
            self,
            submission: LibrarianSubmission = Depends(get_librarian_submission_or_404)
    ):
        await self.manager.reject(self.user, submission)

    @router.put(
        "/{submission_id}/set-work",
        summary="",
    )
    async def set_work_id(
            self,
            request: SetLibrarianSubmissionWork,
            submission: LibrarianSubmission = Depends(get_librarian_submission_or_404)
    ):
        await self.manager.set_work_id(submission, request)

    @router.get(
        "/",
        summary="getting all submissions",
        response_model=list[GetLibrarianSubmission],
    )
    async def get_submissions(
            self,
            filters: LibrarianSubmissionFilter = FilterDepends(LibrarianSubmissionFilter)
    ):
        result = await self.manager.get_submissions(filters)
        return result

    @router.get(
        "/{submission_id}",
        summary="getting submissions by id",
        response_model=GetLibrarianSubmission,
    )
    async def get_submission_by_id(
            self,
            submission: LibrarianSubmission = Depends(get_librarian_submission_or_404)
    ):
        return submission
