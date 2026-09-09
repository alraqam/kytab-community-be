from dataclasses import dataclass
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.managers.edition import EditionManager
from src.backend.catalog.books.managers.work import WorkManager
from src.backend.catalog.books.models import Work
from src.backend.catalog.books.services import DEFAULT_LANGUAGE
from src.backend.catalog.librarian.managers import LibrarianSubmissionManager
from src.backend.catalog.librarian.schemas import CreateLibrarianSubmission
from src.backend.identity.auth.models import User
from src.backend.library.goodreads_import.exceptions import GoodreadsImportRowNotFoundError, \
    ImportRowAlreadySubmittedError, IsNotImportRowOwnerError, InvalidGoodreadsFileError
from src.backend.library.goodreads_import.models import GoodreadsImportRow
from src.backend.library.goodreads_import.parsing import GoodreadsCsvRow, parse_goodreads_csv
from src.backend.library.goodreads_import.repository import GoodreadsImportRowRepository
from src.backend.library.goodreads_import.schemas import GoodreadsImportRowStatus
from src.backend.library.progress.repositories.reading_period import ReadingPeriodRepository
from src.backend.library.reviews.managers.review import ReviewManager
from src.backend.library.reviews.schemas import CreateReview
from src.backend.library.shelf.exceptions import WorkAlreadyInShelfError
from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.managers.shelf_item import ShelfItemManager
from src.backend.library.shelf.schemas import CreateShelfItem


@dataclass
class GoodreadsImportResult:
    """Outcome of a single CSV import, before serialization to GoodreadsImportReport."""

    total_rows: int
    imported_count: int
    skipped_count: int
    unmatched: list[GoodreadsImportRow]


class GoodreadsImportManager:
    """Handles business logic for importing a Goodreads CSV export into a user's library."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.import_row_repo = GoodreadsImportRowRepository(session)
        self.reading_period_repo = ReadingPeriodRepository(session)
        self.work_manager = WorkManager(session)
        self.edition_manager = EditionManager(session)
        self.shelf_manager = ShelfManager(session)
        self.shelf_item_manager = ShelfItemManager(session)
        self.review_manager = ReviewManager(session)
        self.submission_manager = LibrarianSubmissionManager(session)

    async def _find_matching_work(
            self,
            row: GoodreadsCsvRow,
    ) -> Work | None:
        """Looks up the catalog Work a CSV row refers to, by ISBN first, then title+author.

        Args:
            row: Parsed CSV row to match.

        Returns:
            The matching Work, or None when no confident match is found.
        """
        for isbn in (row.isbn13, row.isbn):
            if not isbn:
                continue
            edition = await self.edition_manager.get_edition_by_isbn(isbn)
            if edition:
                return await self.work_manager.get_work_by_id(edition.work_id)

        candidates = await self.work_manager.get_works_by_title(row.title)
        author_lower = row.author.strip().lower()
        matches = [
            work for work in candidates
            if any(author_lower == author.name.strip().lower() for author in work.authors)
        ]
        return matches[0] if len(matches) == 1 else None

    async def _apply_row(
            self,
            user: User,
            work: Work,
            row: GoodreadsCsvRow,
    ) -> bool:
        """Shelves a matched work and records its rating, review, and read dates.

        Args:
            user: User the import is running for.
            work: Catalog Work the row was matched to.
            row: Parsed CSV row with status, rating, review, and dates.

        Returns:
            True if the work was newly shelved; False if it was already on one
            of the user's shelves and was left untouched.
        """
        try:
            shelf = await self.shelf_manager.get_shelf_by_name(user, row.status)
            shelf_item = await self.shelf_item_manager.add_to_shelf(user, shelf, CreateShelfItem(work_id=work.id))
        except WorkAlreadyInShelfError:
            return False

        if row.date_added or row.date_read:
            started_at = datetime.combine(row.date_added, datetime.min.time()) if row.date_added else None
            finished_at = datetime.combine(row.date_read, datetime.min.time()) if row.date_read else None
            await self.reading_period_repo.create_with_dates(shelf_item.id, started_at, finished_at)
            await self.session.commit()

        if row.rating or row.review:
            await self.review_manager.create_review(
                user,
                work,
                CreateReview(rating=row.rating, text=row.review, contains_spoiler=False),
            )

        return True

    async def import_csv(
            self,
            user: User,
            file: UploadFile,
    ) -> GoodreadsImportResult:
        """Imports a Goodreads CSV export into the user's library.

        Matched rows are shelved with their status, rating, review, and read
        dates applied. Unmatched rows are persisted as a report the user can
        submit to the librarian catalog queue one row at a time (FR-CAT-05).

        Args:
            user: User the import is running for.
            file: Uploaded Goodreads CSV export.

        Returns:
            GoodreadsImportResult summarizing imported, skipped, and unmatched rows.

        Raises:
            InvalidGoodreadsFileError: When the file is not a `.csv` file, is not
                valid UTF-8 text, or is missing the columns a Goodreads export has.
        """
        if file.filename and not file.filename.lower().endswith(".csv"):
            raise InvalidGoodreadsFileError("Expected a .csv file")

        content = await file.read()
        rows = parse_goodreads_csv(content)

        imported_count = 0
        skipped_count = 0
        unmatched_rows: list[GoodreadsImportRow] = []

        for row in rows:
            work = await self._find_matching_work(row)
            if work:
                if await self._apply_row(user, work, row):
                    imported_count += 1
                else:
                    skipped_count += 1
                continue

            unmatched_rows.append(
                await self.import_row_repo.create(
                    user_id=user.id,
                    title=row.title,
                    author_name=row.author,
                    isbn=row.isbn13 or row.isbn,
                )
            )

        await self.session.commit()

        return GoodreadsImportResult(
            total_rows=len(rows),
            imported_count=imported_count,
            skipped_count=skipped_count,
            unmatched=unmatched_rows,
        )

    async def submit_row(
            self,
            user: User,
            row: GoodreadsImportRow,
    ) -> GoodreadsImportRow:
        """Submits an unmatched import row to the librarian catalog queue.

        Args:
            user: User requesting the submission; must be the one who ran the import.
            row: GoodreadsImportRow to submit.

        Returns:
            The updated GoodreadsImportRow, now marked submitted.

        Raises:
            IsNotImportRowOwnerError: When the user did not run the import that produced this row.
            ImportRowAlreadySubmittedError: When the row has already been submitted.
        """
        if row.user_id != user.id:
            raise IsNotImportRowOwnerError("Only the importing user can submit this row")

        if row.status != GoodreadsImportRowStatus.unmatched:
            raise ImportRowAlreadySubmittedError("Row has already been submitted to the catalog queue")

        submission = await self.submission_manager.create(
            user,
            CreateLibrarianSubmission(
                title=row.title,
                language=DEFAULT_LANGUAGE,
                author_name=row.author_name,
                isbn=row.isbn,
                cover_url=None,
            ),
        )
        await self.import_row_repo.mark_submitted(row, submission.id)
        await self.session.commit()
        return row

    async def get_my_rows(
            self,
            user: User,
    ) -> list[GoodreadsImportRow]:
        """Lists the current user's Goodreads import rows.

        Args:
            user: User whose import rows are being listed.

        Returns:
            List of matching GoodreadsImportRow instances.
        """
        return await self.import_row_repo.get_user_rows(user.id)

    async def get_row_by_id(
            self,
            row_id: int,
    ) -> GoodreadsImportRow:
        """Fetches a single import row by ID.

        Args:
            row_id: ID of the import row to fetch.

        Returns:
            Matching GoodreadsImportRow instance.

        Raises:
            GoodreadsImportRowNotFoundError: When no import row matches the ID.
        """
        result = await self.import_row_repo.get_by_id(row_id)
        if not result:
            raise GoodreadsImportRowNotFoundError("Import row not found")
        return result
