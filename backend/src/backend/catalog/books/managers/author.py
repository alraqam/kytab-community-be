from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.exceptions import AuthorNotFoundError, WorkNotFoundError, AuthorWorkLinkExistsError
from src.backend.catalog.books.filters import AuthorFilter
from src.backend.catalog.books.models import Author, Work
from src.backend.catalog.books.repository.author import AuthorRepository
from src.backend.catalog.books.repository.work import WorkRepository
from src.backend.catalog.books.schemas.author import CreateAuthor, UpdateAuthor, AddAuthorToWork


class AuthorManager:
    """Handles business logic for Author operations."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.author_repo = AuthorRepository(session)
        self.work_repo = WorkRepository(session)

    async def create_author(
            self,
            request: CreateAuthor,
    ) -> Author:
        """Creates a new author.

        Args:
            request: CreateAuthor payload with name, bio, and photo URL.

        Returns:
            Newly created Author instance.
        """
        author = await self.author_repo.create_author(
            name=request.name,
            bio=request.bio,
            photo_url=request.photo_url,
        )
        await self.session.commit()
        return author

    async def update_author(
            self,
            author_id: int,
            request: UpdateAuthor,
    ) -> Author:
        """Updates an existing author.

        Args:
            author_id: ID of the author to update.
            request: UpdateAuthor payload with optional fields to change.

        Returns:
            Updated Author instance.

        Raises:
            AuthorNotFoundError: When no author with the given ID exists.
        """
        author = await self.get_author_by_id(author_id)
        await self.author_repo.update_author(
            author,
            name=request.name,
            bio=request.bio,
            photo_url=request.photo_url,
        )
        await self.session.commit()
        return author

    async def delete_author(
            self,
            author_id: int,
    ) -> None:
        """Deletes an author.

        Args:
            author_id: ID of the author to delete.

        Raises:
            AuthorNotFoundError: When no author with the given ID exists.
        """
        author = await self.get_author_by_id(author_id)
        await self.author_repo.delete_author(author)
        await self.session.commit()

    async def get_author_by_id(
            self,
            author_id: int,
    ) -> Author:
        """Fetches an author by ID, raising an error if not found.

        Args:
            author_id: ID of the author to retrieve.

        Returns:
            Author instance.

        Raises:
            AuthorNotFoundError: When no author with the given ID exists.
        """
        author = await self.author_repo.get_author_by_id(author_id)
        if not author:
            raise AuthorNotFoundError("Author not found")
        return author

    async def get_all_authors(
            self,
            filters: AuthorFilter | None = None,
    ) -> list[Author]:
        """Returns all authors, optionally filtered and sorted.

        Args:
            filters: Optional AuthorFilter for searching (name) and sorting.

        Returns:
            List of Author instances.
        """
        return await self.author_repo.get_all_authors(filters)

    async def add_author_to_work(
            self,
            request: AddAuthorToWork,
    ) -> None:
        """Links an author to a work.

        Args:
            request: AddAuthorToWork payload with work ID, author ID, and display order.

        Raises:
            WorkNotFoundError: When no work with the given ID exists.
            AuthorNotFoundError: When no author with the given ID exists.
        """
        work = await self.work_repo.get_work_by_id(request.work_id)
        if not work:
            raise WorkNotFoundError("Work not found")
        await self.get_author_by_id(request.author_id)

        try:
            await self.author_repo.add_author_to_work(request.work_id, request.author_id, request.order)
            await self.session.commit()
        except IntegrityError:
            raise AuthorWorkLinkExistsError("Author work link already exists")

    async def remove_author_from_work(
            self,
            work_id: int,
            author_id: int,
    ) -> None:
        """Removes an author-work link.

        Args:
            work_id: ID of the work.
            author_id: ID of the author.
        """
        link = await self.author_repo.get_work_author_link(work_id, author_id)
        if link:
            await self.author_repo.remove_author_from_work(link)
            await self.session.commit()

    async def get_authors_for_work(
            self,
            work_id: int,
    ) -> list[Author]:
        """Returns all authors linked to a work.

        Args:
            work_id: ID of the work.

        Returns:
            List of Author instances.
        """
        return await self.author_repo.get_authors_for_work(work_id)

    async def get_works_for_author(
            self,
            author_id: int,
    ) -> list[Work]:
        """Returns all works linked to an author.

        Args:
            author_id: ID of the author.

        Returns:
            List of Work instances.
        """
        return await self.author_repo.get_works_for_author(author_id)
