from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.managers.work import WorkManager
from src.backend.catalog.books.models import Work
from src.backend.core.dependencies import get_db


async def get_work_manager(
        session: AsyncSession = Depends(get_db)
) -> WorkManager:
    """FastAPI dependency that provides a WorkManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        WorkManager bound to the current session.
    """
    return WorkManager(session)

async def get_work_or_404(
        work_id: int,
        manager: WorkManager = Depends(get_work_manager)
) -> Work:
    """FastAPI dependency that fetches a work by ID or raises if not found.

    Args:
        work_id: Work ID from the path parameter.
        manager: WorkManager injected by get_work_manager.

    Returns:
        Work instance.

    Raises:
        WorkNotFoundError: When no work with the given ID exists.
    """
    return await manager.get_work_by_id(work_id)
