from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.managers.genre import GenreManager
from src.backend.catalog.books.models import Genre
from src.backend.core.dependencies import get_db


async def get_genre_manager(
        session: AsyncSession = Depends(get_db)
) -> GenreManager:
    """FastAPI dependency that provides a GenreManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        GenreManager bound to the current session.
    """
    return GenreManager(session)

async def get_genre_or_404(
        genre_id: int,
        manager: GenreManager = Depends(get_genre_manager)
) -> Genre:
    """FastAPI dependency that fetches a genre by ID or raises if not found.

    Args:
        genre_id: Genre ID from the path parameter.
        manager: GenreManager injected by get_genre_manager.

    Returns:
        Genre instance.

    Raises:
        GenreNotFoundError: When no genre with the given ID exists.
    """
    return await manager.get_genre_by_id(genre_id)
