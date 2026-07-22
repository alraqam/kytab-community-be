from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.exceptions import GenreNotFoundError, WorkNotFoundError, GenreWorkLinkExistsError
from src.backend.catalog.books.filters import GenreFilter
from src.backend.catalog.books.models import Genre, Work
from src.backend.catalog.books.repository.genre import GenreRepository
from src.backend.catalog.books.repository.work import WorkRepository
from src.backend.catalog.books.schemas.genre import CreateGenre, UpdateGenre, AddGenreToWork


class GenreManager:
    """Handles business logic for Genre operations."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.genre_repo = GenreRepository(session)
        self.work_repo = WorkRepository(session)

    async def create_genre(
            self,
            request: CreateGenre,
    ) -> Genre:
        """Creates a new genre.

        Args:
            request: CreateGenre payload with name and slug.

        Returns:
            Newly created Genre instance.
        """
        genre = await self.genre_repo.create_genre(name=request.name, slug=request.slug)
        await self.session.commit()
        return genre

    async def update_genre(
            self,
            genre_id: int,
            request: UpdateGenre,
    ) -> Genre:
        """Updates an existing genre.

        Args:
            genre_id: ID of the genre to update.
            request: UpdateGenre payload with optional name and slug.

        Returns:
            Updated Genre instance.

        Raises:
            GenreNotFoundError: When no genre with the given ID exists.
        """
        genre = await self.get_genre_by_id(genre_id)
        await self.genre_repo.update_genre(genre, name=request.name, slug=request.slug)
        await self.session.commit()
        return genre

    async def delete_genre(
            self,
            genre_id: int,
    ) -> None:
        """Deletes a genre.

        Args:
            genre_id: ID of the genre to delete.

        Raises:
            GenreNotFoundError: When no genre with the given ID exists.
        """
        genre = await self.get_genre_by_id(genre_id)
        await self.genre_repo.delete_genre(genre)
        await self.session.commit()

    async def get_genre_by_id(
            self,
            genre_id: int,
    ) -> Genre:
        """Fetches a genre by ID, raising an error if not found.

        Args:
            genre_id: ID of the genre to retrieve.

        Returns:
            Genre instance.

        Raises:
            GenreNotFoundError: When no genre with the given ID exists.
        """
        genre = await self.genre_repo.get_genre_by_id(genre_id)
        if not genre:
            raise GenreNotFoundError("Genre not found")
        return genre

    async def get_all_genres(
            self,
            filters: GenreFilter | None = None,
    ) -> list[Genre]:
        """Returns all genres, optionally filtered and sorted.

        Args:
            filters: Optional GenreFilter for searching (name/slug) and sorting.

        Returns:
            List of Genre instances.
        """
        return await self.genre_repo.get_all_genres(filters)

    async def add_genre_to_work(
            self,
            request: AddGenreToWork,
    ) -> None:
        """Links a genre to a work.

        Args:
            request: AddGenreToWork payload with work ID and genre ID.

        Raises:
            WorkNotFoundError: When no work with the given ID exists.
            GenreNotFoundError: When no genre with the given ID exists.
        """
        work = await self.work_repo.get_work_by_id(request.work_id)
        if not work:
            raise WorkNotFoundError("Work not found")
        await self.get_genre_by_id(request.genre_id)
        try:
            await self.genre_repo.add_genre_to_work(request.work_id, request.genre_id)
            await self.session.commit()
        except IntegrityError:
            raise GenreWorkLinkExistsError("Genre work link already exists")

    async def remove_genre_from_work(
            self,
            work_id: int,
            genre_id: int,
    ) -> None:
        """Removes a work-genre link.

        Args:
            work_id: ID of the work.
            genre_id: ID of the genre.
        """
        link = await self.genre_repo.get_work_genre_link(work_id, genre_id)
        if link:
            await self.genre_repo.remove_genre_from_work(link)
            await self.session.commit()

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
        return await self.genre_repo.get_genres_for_work(work_id)

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
        return await self.genre_repo.get_works_for_genre(genre_id)
