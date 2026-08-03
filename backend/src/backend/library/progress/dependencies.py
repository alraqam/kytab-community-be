from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.dependencies import  get_shelf_item_or_404
from src.backend.identity.auth.models import User
from src.backend.core.dependencies import get_db
from src.backend.library.progress.exceptions import IsNotProgressLogOwnerError, ReadingPeriodNotInShelfItemError, \
    ProgressLogNotInReadingPeriodError
from src.backend.library.progress.models import ProgressLog, ReadingPeriod


from src.backend.library.progress.managers.reading_period import ReadingPeriodManager

async def get_reading_period_manager(
        session: AsyncSession = Depends(get_db)
) -> ReadingPeriodManager:
    """FastAPI dependency that provides a ReadingPeriodManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        ReadingPeriodManager bound to the current session.
    """
    return ReadingPeriodManager(session)

async def get_reading_period_or_404(
        reading_period_id: int,
        shelf_item = Depends(get_shelf_item_or_404),
        manager: ReadingPeriodManager = Depends(get_reading_period_manager)
) -> ReadingPeriod:
    """FastAPI dependency that resolves a reading period by ID, scoped to a shelf item.

    Args:
        reading_period_id: ID of the reading period to fetch.
        shelf_item: ShelfItem the reading period is expected to belong to.
        manager: ReadingPeriodManager used to fetch the reading period.

    Returns:
        Matching ReadingPeriod instance.

    Raises:
        ReadingPeriodNotFound: When no reading period matches the ID.
        ReadingPeriodNotInShelfItemError: When the reading period does not belong to the given shelf item.
    """
    reading_period = await manager.get_reading_period_by_id(reading_period_id)
    if reading_period.shelf_item_id != shelf_item.id:
        raise ReadingPeriodNotInShelfItemError("Reading period item not found in this shelf item")
    return reading_period

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
        reading_period = Depends(get_reading_period_or_404),
        manager: ProgressLogManager = Depends(get_progress_log_manager)
) -> ProgressLog:
    """FastAPI dependency that resolves a progress log by ID, scoped to a reading period.

    Args:
        log_id: ID of the progress log to fetch.
        reading_period: ReadingPeriod the log is expected to belong to.
        manager: ProgressLogManager used to fetch the log.

    Returns:
        Matching ProgressLog instance.

    Raises:
        ProgressLogNotFound: When no progress log matches the ID.
        ProgressLogNotInReadingPeriodError: When the log does not belong to the given reading period.
    """
    log = await manager.get_progress_log_by_id(log_id)
    if log.period_id != reading_period.id:
        raise ProgressLogNotInReadingPeriodError("Progress log not found in this reading period")
    return log
