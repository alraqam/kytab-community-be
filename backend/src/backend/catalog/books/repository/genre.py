from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.filters import GenreFilter
from src.backend.catalog.books.models import Genre, WorkGenre, Work


@dataclass
class GenreRepository:
    """Data access layer for Genre model operations."""

    session: AsyncSession

    async def create_genre(
            self,
            name: str,
            slug: str,
    ) -> Genre:
        """Creates and persists a new genre record.

        Args:
            name: Genre display name.
            slug: URL-safe unique identifier for the genre.

        Returns:
            Newly created Genre instance.
        """
        genre = Genre(name=name, slug=slug)
        self.session.add(genre)
        await self.session.flush()
        return genre

    async def update_genre(
            self,
            genre: Genre,
            name: str | None = None,
            slug: str | None = None,
    ) -> None:
        """Updates non-None fields on the genre and flushes the session.

        Args:
            genre: Genre instance to update.
            name: New name, or None to leave unchanged.
            slug: New slug, or None to leave unchanged.
        """
        updates = {
            "name": name,
            "slug": slug,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(genre, field, value)
        await self.session.flush()

    async def delete_genre(
            self,
            genre: Genre,
    ) -> None:
        """Deletes the genre record and flushes the session.

        Args:
            genre: Genre instance to delete.
        """
        await self.session.delete(genre)
        await self.session.flush()

    async def get_genre_by_id(
            self,
            genre_id: int,
    ) -> Genre | None:
        """Fetches a genre by its internal ID.

        Args:
            genre_id: Internal database ID.

        Returns:
            Genre instance if found, None otherwise.
        """
        stmt = select(Genre).where(Genre.id == genre_id)
        result = await self.session.execute(stmt)
        genre = result.scalar_one_or_none()
        return genre

    async def get_genre_by_slug(
            self,
            slug: str,
    ) -> Genre | None:
        """Fetches a genre by its slug.

        Args:
            slug: URL-safe genre identifier.

        Returns:
            Genre instance if found, None otherwise.
        """
        stmt = select(Genre).where(Genre.slug == slug)
        result = await self.session.execute(stmt)
        genre = result.scalar_one_or_none()
        return genre

    async def get_all_genres(
            self,
            filters: GenreFilter | None = None,
    ) -> list[Genre]:
        """Returns all genre records, optionally filtered and sorted.

        Args:
            filters: Optional GenreFilter for searching (name/slug) and sorting.

        Returns:
            List of Genre instances.
        """
        stmt = select(Genre)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        genres =  list(result.scalars().all())
        return genres

    async def add_genre_to_work(
            self,
            work_id: int,
            genre_id: int,
    ) -> WorkGenre:
        """Links a genre to a work.

        Args:
            work_id: ID of the work.
            genre_id: ID of the genre.

        Returns:
            Newly created WorkGenre link instance.
        """
        link = WorkGenre(
            work_id=work_id,
            genre_id=genre_id,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_work_genre_link(
            self,
            work_id: int,
            genre_id: int,
    ) -> WorkGenre | None:
        """Fetches the link record between a work and a genre.

        Args:
            work_id: ID of the work.
            genre_id: ID of the genre.

        Returns:
            WorkGenre instance if found, None otherwise.
        """
        stmt = select(WorkGenre).where(
            and_(
                WorkGenre.work_id == work_id,
                WorkGenre.genre_id == genre_id,
            )
        )
        result = await self.session.execute(stmt)
        work = result.scalar_one_or_none()
        return work

    async def remove_genre_from_work(
            self,
            link: WorkGenre,
    ) -> None:
        """Removes a work-genre link and flushes the session.

        Args:
            link: WorkGenre instance to delete.
        """
        await self.session.delete(link)
        await self.session.flush()

    async def get_genres_for_work(
            self,
            work_id: int,
    ) -> list[Genre]:
        """Returns all genres linked to a work.

        Args:
            work_id: ID of the work.

        Returns:
            List of Genre instances.
        """
        stmt = (
            select(Genre)
            .join(WorkGenre, WorkGenre.genre_id == Genre.id)
            .where(WorkGenre.work_id == work_id)
        )
        result = await self.session.execute(stmt)
        works = list(result.scalars().all())
        return works

    async def get_works_for_genre(
            self,
            genre_id: int,
    ) -> list[Work]:
        """Returns all works tagged with a genre.

        Args:
            genre_id: ID of the genre.

        Returns:
            List of Work instances.
        """
        stmt = (
            select(Work)
            .join(WorkGenre, WorkGenre.work_id == Work.id)
            .where(WorkGenre.genre_id == genre_id)
        )
        result = await self.session.execute(stmt)
        works = list(result.scalars().all())
        return works
