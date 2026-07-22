from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.managers.series import SeriesManager
from src.backend.catalog.books.models import Series
from src.backend.core.dependencies import get_db


async def get_series_manager(
        session: AsyncSession = Depends(get_db)
) -> SeriesManager:
    """FastAPI dependency that provides a SeriesManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        SeriesManager bound to the current session.
    """
    return SeriesManager(session)

async def get_series_or_404(
        series_id: int,
        manager: SeriesManager = Depends(get_series_manager)
) -> Series:
    """FastAPI dependency that fetches a series by ID or raises if not found.

    Args:
        series_id: Series ID from the path parameter.
        manager: SeriesManager injected by get_series_manager.

    Returns:
        Series instance.

    Raises:
        SeriesNotFoundError: When no series with the given ID exists.
    """
    return await manager.get_series_by_id(series_id)
