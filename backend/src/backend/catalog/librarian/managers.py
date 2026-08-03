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
    """Handles business logic for librarian submission review workflow: creation, approval, rejection, and linking to a catalog work."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.submission_repo = LibrarianSubmissionRepository(session)
        self.work_manager = WorkManager(session)


    async def create(
            self,
            user: User,
            request: CreateLibrarianSubmission,
    ) -> LibrarianSubmission:
        """Creates a new pending librarian submission on behalf of a user.

        Args:
            user: User submitting the book proposal.
            request: CreateLibrarianSubmission payload with book details.

        Returns:
            Newly created LibrarianSubmission instance.
        """
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
        """Approves a pending submission.

        Args:
            user: Librarian approving the submission.
            submission: LibrarianSubmission instance to approve.

        Raises:
            LibrarySubmissionStatusError: When the submission is not pending.
        """
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
        """Rejects a pending submission.

        Args:
            user: Librarian rejecting the submission.
            submission: LibrarianSubmission instance to reject.

        Raises:
            LibrarySubmissionStatusError: When the submission is not pending.
        """
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
        """Links an approved submission to the catalog work it produced.

        Args:
            submission: LibrarianSubmission instance to update.
            request: SetLibrarianSubmissionWork payload with the resulting work ID.

        Raises:
            LibrarySubmissionStatusError: When the submission is not approved.
            WorkNotFoundError: When no work with the given ID exists.
        """
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
        """Lists librarian submissions matching the given filters.

        Args:
            filters: LibrarianSubmissionFilter with search, status, and ordering criteria.

        Returns:
            List of matching LibrarianSubmission instances.
        """
        result = await self.submission_repo.get_submissions(
            filters=filters
        )
        return result

    async def get_submission_by_id(
            self,
            submission_id: int
    ) -> LibrarianSubmission:
        """Fetches a submission by ID, raising an error if not found.

        Args:
            submission_id: ID of the submission to retrieve.

        Returns:
            LibrarianSubmission instance.

        Raises:
            LibrarianSubmissionNotFoundError: When no submission with the given ID exists.
        """
        result = await self.submission_repo.get_submission_by_id(
            submission_id=submission_id
        )
        if not result:
            raise LibrarianSubmissionNotFoundError("Librarian submission not found")
        return result
