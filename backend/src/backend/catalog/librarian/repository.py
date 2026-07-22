from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.librarian.filters import LibrarianSubmissionFilter
from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.catalog.librarian.schemas import LibrarianSubmissionStatus


@dataclass
class LibrarianSubmissionRepository:
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
        submission.resulting_work_id = work_id
        self.session.add(submission)
        await self.session.flush()

    async def get_submissions(
            self,
            filters: LibrarianSubmissionFilter | None = None
    ) -> list[LibrarianSubmission]:
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
        stmt = select(LibrarianSubmission).where(LibrarianSubmission.id == submission_id)
        result = await self.session.execute(stmt)
        submission = result.scalar_one_or_none()
        return submission
