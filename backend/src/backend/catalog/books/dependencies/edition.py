from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.managers.edition import EditionManager
from src.backend.catalog.books.models import Edition
from src.backend.core.dependencies import get_db


async def get_edition_manager(
        session: AsyncSession = Depends(get_db)
) -> EditionManager:
    """FastAPI dependency that provides an EditionManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        EditionManager bound to the current session.
    """
    return EditionManager(session)

async def get_edition_or_404(
        edition_id: int,
        manager: EditionManager = Depends(get_edition_manager)
) -> Edition:
    """FastAPI dependency that fetches an edition by ID or raises if not found.

    Args:
        edition_id: Edition ID from the path parameter.
        manager: EditionManager injected by get_edition_manager.

    Returns:
        Edition instance.

    Raises:
        EditionNotFoundError: When no edition with the given ID exists.
    """
    return await manager.get_edition_by_id(edition_id)
