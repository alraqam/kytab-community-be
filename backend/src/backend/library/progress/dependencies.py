from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.core.dependencies import get_db
from src.backend.library.progress.exceptions import IsNotProgressLogOwnerError
from src.backend.library.progress.models import ProgressLog, ReadingPeriod


async def is_log_owner(
        user: User,
        log: ProgressLog,
) -> None:
    """Verifies that the user owns the progress log.

    Args:
        user: Authenticated user to check.
        log: ProgressLog instance to verify ownership of.

    Raises:
        IsNotProgressLogOwnerError: When the user is not the owner of the log.
    """
    if log.user_id != user.id:
        raise IsNotProgressLogOwnerError("Only log owners can access and change their list")
    return

from src.backend.library.progress.managers.progress_logs import ProgressLogManager

async def get_progress_log_manager(
        session: AsyncSession = Depends(get_db)
) -> ProgressLogManager:
    """FastAPI dependency that provides a ProgressLogManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        ProgressLogManager bound to the current session.
    """
    return ProgressLogManager(session)

async def get_progress_log_or_404(
        log_id: int,
        manager: ProgressLogManager = Depends(get_progress_log_manager)
) -> ProgressLog:
    """FastAPI dependency that fetches a progress log by ID or raises if not found.

    Args:
        log_id: Progress log ID from the path parameter.
        manager: ProgressLogManager injected by get_progress_log_manager.

    Returns:
        ProgressLog instance.

    Raises:
        ProgressLogNotFound: When no log with the given ID exists.
    """
    return await manager.get_progress_log_by_id(log_id)


from src.backend.library.progress.managers.reading_period import ReadingPeriodManager

async def get_reading_period_manager(
        session: AsyncSession = Depends(get_db)
) -> ReadingPeriodManager:
    return ReadingPeriodManager(session)

async def get_reading_period_or_404(
        reading_period_id: int,
        manager: ReadingPeriodManager = Depends(get_reading_period_manager)
) -> ReadingPeriod:
    return await manager.get_reading_period_by_id(reading_period_id)