from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.analytics.managers import ClubAnalyticsManager
from src.backend.core.dependencies import get_db


async def get_club_analytics_manager(
        session: AsyncSession = Depends(get_db)
) -> ClubAnalyticsManager:
    return ClubAnalyticsManager(session)
