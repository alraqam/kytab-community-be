from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.catalog.books.managers.work import WorkManager
from src.backend.catalog.librarian.exceptions import LibrarianSubmissionNotFoundError, LibrarySubmissionStatusError
from src.backend.catalog.librarian.filters import LibrarianSubmissionFilter
from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.catalog.librarian.repository import LibrarianSubmissionRepository
from src.backend.catalog.librarian.schemas import CreateLibrarianSubmission, LibrarianSubmissionStatus, \
    SetLibrarianSubmissionWork


class LibrarianSubmissionManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.submission_repo = LibrarianSubmissionRepository(session)
        self.work_manager = WorkManager(session)


    async def create(
            self,
            user: User,
            request: CreateLibrarianSubmission,
    ) -> LibrarianSubmission:
        result = await self.submission_repo.create(
            submitted_by_id=user.id,
            title=request.title,
            language=request.language,
            author_name=request.author_name,
            isbn=request.isbn,
            cover_url=request.cover_url,
        )
        await self.session.commit()
        return result


    async def approve(
            self,
            user: User,
            submission: LibrarianSubmission
    ) -> None:
        if submission.status != LibrarianSubmissionStatus.pending:
            raise LibrarySubmissionStatusError("Only submissions with pending status can be changed")

        await self.submission_repo.update_status(
            submission=submission,
            status=LibrarianSubmissionStatus.approved,
            reviewed_by_id=user.id
        )
        await self.session.commit()

    async def reject(
            self,
            user: User,
            submission: LibrarianSubmission
    ) -> None:
        if submission.status != LibrarianSubmissionStatus.pending:
            raise LibrarySubmissionStatusError("Only submissions with pending status can be changed")

        await self.submission_repo.update_status(
            submission=submission,
            status=LibrarianSubmissionStatus.rejected,
            reviewed_by_id=user.id
        )
        await self.session.commit()

    async def set_work_id(
            self,
            submission: LibrarianSubmission,
            request: SetLibrarianSubmissionWork
    ) -> None:
        if submission.status != LibrarianSubmissionStatus.approved:
            raise LibrarySubmissionStatusError("Only approved submissions can have work id")

        work = await self.work_manager.get_work_by_id(request.resulting_work_id)

        await self.submission_repo.update_resulting_work(
            submission=submission,
            work_id=work.id,
        )
        await self.session.commit()

    async def get_submissions(
            self,
            filters: LibrarianSubmissionFilter
    ) -> list[LibrarianSubmission]:
        result = await self.submission_repo.get_submissions(
            filters=filters
        )
        return result

    async def get_submission_by_id(
            self,
            submission_id: int
    ) -> LibrarianSubmission:
        result = await self.submission_repo.get_submission_by_id(
            submission_id=submission_id
        )
        if not result:
            raise LibrarianSubmissionNotFoundError("Librarian submission not found")
        return result
