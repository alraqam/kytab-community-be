from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.filters import AuthorFilter
from src.backend.catalog.books.models import Author, WorkAuthor, Work


@dataclass
class AuthorRepository:
    """Data access layer for Author model operations."""

    session: AsyncSession

    async def create_author(
            self,
            name: str,
            bio: str | None = None,
            photo_url: str | None = None,
    ) -> Author:
        """Creates and persists a new author record.

        Args:
            name: Author's name.
            bio: Optional biography text.
            photo_url: Optional photo URL.

        Returns:
            Newly created Author instance.
        """
        author = Author(
            name=name,
            bio=bio,
            photo_url=photo_url,
        )
        self.session.add(author)
        await self.session.flush()
        return author

    async def update_author(
            self,
            author: Author,
            name: str | None = None,
            bio: str | None = None,
            photo_url: str | None = None,
    ) -> None:
        """Updates non-None fields on the author and flushes the session.

        Args:
            author: Author instance to update.
            name: New name, or None to leave unchanged.
            bio: New biography, or None to leave unchanged.
            photo_url: New photo URL, or None to leave unchanged.
        """
        updates = {
            "name": name,
            "bio": bio,
            "photo_url": photo_url,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(author, field, value)
        await self.session.flush()

    async def delete_author(
            self,
            author: Author,
    ) -> None:
        """Deletes the author record and flushes the session.

        Args:
            author: Author instance to delete.
        """
        await self.session.delete(author)
        await self.session.flush()

    async def get_author_by_id(
            self,
            author_id: int,
    ) -> Author | None:
        """Fetches an author by its internal ID.

        Args:
            author_id: Internal database ID.

        Returns:
            Author instance if found, None otherwise.
        """
        stmt = select(Author).where(Author.id == author_id)
        result = await self.session.execute(stmt)
        author = result.scalar_one_or_none()
        return author

    async def get_all_authors(
            self,
            filters: AuthorFilter | None = None,
    ) -> list[Author]:
        """Returns all author records, optionally filtered and sorted.

        Args:
            filters: Optional AuthorFilter for searching (name) and sorting.

        Returns:
            List of Author instances.
        """
        stmt = select(Author)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        authors =  list(result.scalars().all())
        return authors

    async def get_author_by_name(
            self,
            name: str,
    ) -> Author | None:
        """Fetches an author by exact name match.

        Args:
            name: Author's name.

        Returns:
            Author instance if found, None otherwise.
        """
        stmt = select(Author).where(Author.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_author_to_work(
            self,
            work_id: int,
            author_id: int,
            order: int | None = None,
    ) -> WorkAuthor:
        """Links an author to a work.

        Args:
            work_id: ID of the work.
            author_id: ID of the author.
            order: Optional display order among the work's authors.

        Returns:
            Newly created WorkAuthor link instance.
        """
        link = WorkAuthor(
            work_id=work_id,
            author_id=author_id,
            order=order,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_work_author_link(
            self,
            work_id: int,
            author_id: int,
    ) -> WorkAuthor | None:
        """Fetches the link record between a work and an author.

        Args:
            work_id: ID of the work.
            author_id: ID of the author.

        Returns:
            WorkAuthor instance if found, None otherwise.
        """
        stmt = select(WorkAuthor).where(
            and_(
                WorkAuthor.work_id == work_id,
                WorkAuthor.author_id == author_id,
            )
        )
        result = await self.session.execute(stmt)
        work = result.scalar_one_or_none()
        return work

    async def remove_author_from_work(
            self,
            link: WorkAuthor,
    ) -> None:
        """Removes an author-work link and flushes the session.

        Args:
            link: WorkAuthor instance to delete.
        """
        await self.session.delete(link)
        await self.session.flush()

    async def get_authors_for_work(
            self,
            work_id: int,
    ) -> list[Author]:
        """Returns all authors linked to a work, ordered by display order.

        Args:
            work_id: ID of the work.

        Returns:
            List of Author instances.
        """
        stmt = (
            select(Author)
            .join(WorkAuthor, WorkAuthor.author_id == Author.id)
            .where(WorkAuthor.work_id == work_id)
            .order_by(WorkAuthor.order)
        )
        result = await self.session.execute(stmt)
        works =  list(result.scalars().all())
        return works

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
        stmt = (
            select(Work)
            .join(WorkAuthor, WorkAuthor.work_id == Work.id)
            .where(WorkAuthor.author_id == author_id)
        )
        result = await self.session.execute(stmt)
        works =  list(result.scalars().all())
        return works