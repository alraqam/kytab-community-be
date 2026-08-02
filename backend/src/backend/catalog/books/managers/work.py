from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.exceptions import WorkNotFoundError, DuplicateMergeError
from src.backend.catalog.books.filters import WorkFilter
from src.backend.catalog.books.models import Work
from src.backend.catalog.books.repository.work import WorkRepository
from src.backend.catalog.books.schemas.work import CreateWork, UpdateWork


class WorkManager:
    """Handles business logic for Work operations."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.work_repo = WorkRepository(session)

    async def create_work(
            self,
            request: CreateWork,
    ) -> Work:
        """Creates a new work.

        Args:
            request: CreateWork payload with title, description, and language.

        Returns:
            Newly created Work instance.
        """
        work = await self.work_repo.create_work(
            canonical_title=request.canonical_title,
            description=request.description,
            primary_language=request.primary_language,
        )
        await self.session.commit()
        return work

    async def update_work(
            self,
            work_id: int,
            request: UpdateWork,
    ) -> Work:
        """Updates an existing work.

        Args:
            work_id: ID of the work to update.
            request: UpdateWork payload with optional title, description, and language.

        Returns:
            Updated Work instance.

        Raises:
            WorkNotFoundError: When no work with the given ID exists.
        """
        work = await self.get_work_by_id(work_id)
        await self.work_repo.update_work(
            work,
            canonical_title=request.canonical_title,
            description=request.description,
            primary_language=request.primary_language,
        )
        await self.session.commit()
        return work

    async def delete_work(
            self,
            work_id: int,
    ) -> None:
        """Deletes a work.

        Args:
            work_id: ID of the work to delete.

        Raises:
            WorkNotFoundError: When no work with the given ID exists.
        """
        work = await self.get_work_by_id(work_id)
        await self.work_repo.delete_work(work)
        await self.session.commit()

    async def get_work_by_id(
            self,
            work_id: int,
    ) -> Work:
        """Fetches a work by ID, raising an error if not found.

        Args:
            work_id: ID of the work to retrieve.

        Returns:
            Work instance.

        Raises:
            WorkNotFoundError: When no work with the given ID exists.
        """
        work = await self.work_repo.get_work_by_id(work_id)
        if not work:
            raise WorkNotFoundError("Work not found")
        return work

    async def get_all_works(
            self,
            filters: WorkFilter | None = None,
    ) -> list[Work]:
        """Returns all works, optionally filtered and sorted.

        Args:
            filters: Optional WorkFilter for searching (title/description) and sorting.

        Returns:
            List of Work instances.
        """
        return await self.work_repo.get_all_works(filters)

    async def merge_works(
            self,
            source_work_id: int,
            target_work_id: int,
    ) -> Work:
        """Merges a duplicate work into the canonical target work.

        Editions, shelf items, reviews, reading sessions, and author/genre/series
        links are reassigned to the target before the duplicate is deleted.

        Args:
            source_work_id: ID of the duplicate work to merge away.
            target_work_id: ID of the canonical work to keep.

        Returns:
            The canonical target Work instance.

        Raises:
            DuplicateMergeError: When source and target are the same work.
            WorkNotFoundError: When either work does not exist.
        """
        if source_work_id == target_work_id:
            raise DuplicateMergeError("Cannot merge a work into itself")

        source = await self.get_work_by_id(source_work_id)
        target = await self.get_work_by_id(target_work_id)

        await self.work_repo.merge_works(source.id, target.id)
        await self.work_repo.delete_work(source)
        await self.session.commit()
        return target
