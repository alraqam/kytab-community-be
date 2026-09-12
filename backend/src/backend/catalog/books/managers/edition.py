from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.exceptions import WorkNotFoundError, EditionNotFoundError
from src.backend.catalog.books.filters import EditionFilter
from src.backend.catalog.books.models import Edition
from src.backend.catalog.books.repository.edition import EditionRepository
from src.backend.catalog.books.repository.work import WorkRepository
from src.backend.catalog.books.schemas.edition import CreateEdition, UpdateEdition


class EditionManager:
    """Handles business logic for Edition operations."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.edition_repo = EditionRepository(session)
        self.work_repo = WorkRepository(session)

    async def create_edition(
            self,
            request: CreateEdition,
    ) -> Edition:
        """Creates a new edition under a work.

        Args:
            request: CreateEdition payload with the parent work ID and edition details.

        Returns:
            Newly created Edition instance.

        Raises:
            WorkNotFoundError: When no work with the given ID exists.
        """
        work = await self.work_repo.get_work_by_id(request.work_id)
        if not work:
            raise WorkNotFoundError("Work not found")

        edition = await self.edition_repo.create_edition(
            work_id=request.work_id,
            title=request.title,
            language=request.language,
            google_books_id=request.google_books_id,
            open_library_id=request.open_library_id,
            publisher=request.publisher,
            published_year=request.published_year,
            pages_count=request.pages_count,
            isbn=request.isbn,
            cover_url=request.cover_url,
            is_primary=request.is_primary,
        )
        await self.session.commit()
        return await self.edition_repo.get_edition_by_id(edition.id)

    async def update_edition(
            self,
            edition_id: int,
            request: UpdateEdition,
    ) -> Edition:
        """Updates an existing edition.

        Args:
            edition_id: ID of the edition to update.
            request: UpdateEdition payload with optional fields to change.

        Returns:
            Updated Edition instance.

        Raises:
            EditionNotFoundError: When no edition with the given ID exists.
        """
        edition = await self.get_edition_by_id(edition_id)
        await self.edition_repo.update_edition(
            edition,
            title=request.title,
            language=request.language,
            publisher=request.publisher,
            published_year=request.published_year,
            pages_count=request.pages_count,
            isbn=request.isbn,
            cover_url=request.cover_url,
            is_primary=request.is_primary,
        )
        await self.session.commit()
        return edition

    async def delete_edition(
            self,
            edition_id: int,
    ) -> None:
        """Deletes an edition.

        Args:
            edition_id: ID of the edition to delete.

        Raises:
            EditionNotFoundError: When no edition with the given ID exists.
        """
        edition = await self.get_edition_by_id(edition_id)
        await self.edition_repo.delete_edition(edition)
        await self.session.commit()

    async def get_edition_by_id(
            self,
            edition_id: int,
    ) -> Edition:
        """Fetches an edition by ID, raising an error if not found.

        Args:
            edition_id: ID of the edition to retrieve.

        Returns:
            Edition instance.

        Raises:
            EditionNotFoundError: When no edition with the given ID exists.
        """
        edition = await self.edition_repo.get_edition_by_id(edition_id)
        if not edition:
            raise EditionNotFoundError("Edition not found")
        return edition

    async def get_editions_by_work(
            self,
            work_id: int,
    ) -> list[Edition]:
        """Returns all editions belonging to a work.

        Args:
            work_id: ID of the parent Work.

        Returns:
            List of Edition instances.
        """
        return await self.edition_repo.get_editions_by_work(work_id)

    async def get_edition_by_isbn(
            self,
            isbn: str,
    ) -> Edition | None:
        """Fetches an edition by its ISBN.

        Args:
            isbn: ISBN string to search for.

        Returns:
            Edition instance if found, None otherwise.
        """
        return await self.edition_repo.get_edition_by_isbn(isbn)

    async def get_all_editions(
            self,
            filters: EditionFilter | None = None,
    ) -> list[Edition]:
        """Returns all editions, optionally filtered and sorted.

        Args:
            filters: Optional EditionFilter for filtering (work_id/language/title/isbn) and sorting.

        Returns:
            List of Edition instances.
        """
        return await self.edition_repo.get_all_editions(filters)
