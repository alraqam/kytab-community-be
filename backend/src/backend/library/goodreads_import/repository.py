from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.goodreads_import.models import GoodreadsImportRow
from src.backend.library.goodreads_import.schemas import GoodreadsImportRowStatus


@dataclass
class GoodreadsImportRowRepository:
    """Data-access layer for Goodreads import row persistence and queries."""

    session: AsyncSession

    async def create(
            self,
            user_id: int,
            title: str,
            author_name: str,
            isbn: str | None,
    ) -> GoodreadsImportRow:
        """Inserts a new unmatched import row.

        Args:
            user_id: ID of the user who ran the import.
            title: Title as it appeared in the CSV row.
            author_name: Author name as it appeared in the CSV row.
            isbn: ISBN as it appeared in the CSV row, if any.

        Returns:
            Newly created GoodreadsImportRow instance.
        """
        result = GoodreadsImportRow(
            user_id=user_id,
            title=title,
            author_name=author_name,
            isbn=isbn,
            status=GoodreadsImportRowStatus.unmatched,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def mark_submitted(
            self,
            row: GoodreadsImportRow,
            submission_id: int,
    ) -> None:
        """Marks a row as submitted to the librarian catalog queue.

        Args:
            row: GoodreadsImportRow instance to update.
            submission_id: ID of the resulting LibrarianSubmission.
        """
        row.status = GoodreadsImportRowStatus.submitted
        row.submission_id = submission_id
        self.session.add(row)
        await self.session.flush()

    async def get_by_id(
            self,
            row_id: int,
    ) -> GoodreadsImportRow | None:
        """Fetches a single import row by ID.

        Args:
            row_id: ID of the import row to fetch.

        Returns:
            Matching GoodreadsImportRow instance, or None if not found.
        """
        stmt = select(GoodreadsImportRow).where(GoodreadsImportRow.id == row_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return row

    async def get_user_rows(
            self,
            user_id: int,
    ) -> list[GoodreadsImportRow]:
        """Lists all import rows belonging to a user.

        Args:
            user_id: ID of the user whose import rows are being listed.

        Returns:
            List of matching GoodreadsImportRow instances.
        """
        stmt = select(GoodreadsImportRow).where(GoodreadsImportRow.user_id == user_id)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows
