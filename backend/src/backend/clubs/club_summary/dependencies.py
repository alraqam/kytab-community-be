from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_summary.managers import ClubSummaryManager
from src.backend.core.dependencies import get_db


async def get_club_summary_manager(
        session: AsyncSession = Depends(get_db)
) -> ClubSummaryManager:
    """Builds a ClubSummaryManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        ClubSummaryManager instance.
    """
    return ClubSummaryManager(session)
