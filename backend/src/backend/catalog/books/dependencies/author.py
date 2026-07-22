from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.managers.author import AuthorManager
from src.backend.catalog.books.models import Author
from src.backend.core.dependencies import get_db


async def get_author_manager(
        session: AsyncSession = Depends(get_db)
) -> AuthorManager:
    """FastAPI dependency that provides an AuthorManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        AuthorManager bound to the current session.
    """
    return AuthorManager(session)

async def get_author_or_404(
        author_id: int,
        manager: AuthorManager = Depends(get_author_manager)
) -> Author:
    """FastAPI dependency that fetches an author by ID or raises if not found.

    Args:
        author_id: Author ID from the path parameter.
        manager: AuthorManager injected by get_author_manager.

    Returns:
        Author instance.

    Raises:
        AuthorNotFoundError: When no author with the given ID exists.
    """
    return await manager.get_author_by_id(author_id)
