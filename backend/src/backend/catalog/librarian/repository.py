from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.librarian.filters import LibrarianSubmissionFilter
from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.catalog.librarian.schemas import LibrarianSubmissionStatus


@dataclass
class LibrarianSubmissionRepository:
    """Data access layer for LibrarianSubmission persistence and queries."""

    session: AsyncSession

    async def create(
            self,
            submitted_by_id: int,
            title: str,
            language: str,
            author_name: str,
            isbn: str | None = None,
            cover_url: str | None = None,
    ) -> LibrarianSubmission:
        """Inserts a new submission with pending status.

        Args:
            submitted_by_id: ID of the user submitting the proposal.
            title: Proposed book title.
            language: Language of the proposed book.
            author_name: Name of the proposed book's author.
            isbn: Optional ISBN.
            cover_url: Optional cover image URL.

        Returns:
            Newly created LibrarianSubmission instance.
        """
        result = LibrarianSubmission(
            submitted_by_id=submitted_by_id,
            title=title,
            language=language,
            author_name=author_name,
            isbn=isbn,
            cover_url=cover_url,
            status=LibrarianSubmissionStatus.pending
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_status(
            self,
            submission: LibrarianSubmission,
            status: str,
            reviewed_by_id: int
    ) -> None:
        """Sets a submission's status and stamps the reviewer and review time.

        Args:
            submission: LibrarianSubmission instance to update.
            status: New status value.
            reviewed_by_id: ID of the librarian performing the review.
        """
        submission.status = status
        submission.reviewed_by_id = reviewed_by_id
        submission.reviewed_at = datetime.now()
        self.session.add(submission)
        await self.session.flush()

    async def update_resulting_work(
            self,
            submission: LibrarianSubmission,
            work_id: int
    ) -> None:
        """Sets the catalog work ID produced by a submission.

        Args:
            submission: LibrarianSubmission instance to update.
            work_id: ID of the resulting catalog Work.
        """
        submission.resulting_work_id = work_id
        self.session.add(submission)
        await self.session.flush()

    async def get_submissions(
            self,
            filters: LibrarianSubmissionFilter | None = None
    ) -> list[LibrarianSubmission]:
        """Lists submissions, optionally filtered and sorted.

        Args:
            filters: LibrarianSubmissionFilter to apply, or None for no filtering.

        Returns:
            List of matching LibrarianSubmission instances.
        """
        stmt = select(LibrarianSubmission)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        submissions = list(result.scalars().all())
        return submissions

    async def get_submission_by_id(
            self,
            submission_id: int
    ) -> LibrarianSubmission | None:
        """Fetches a submission by ID.

        Args:
            submission_id: ID of the submission to fetch.

        Returns:
            Matching LibrarianSubmission instance, or None if not found.
        """
        stmt = select(LibrarianSubmission).where(LibrarianSubmission.id == submission_id)
        result = await self.session.execute(stmt)
        submission = result.scalar_one_or_none()
        return submission
