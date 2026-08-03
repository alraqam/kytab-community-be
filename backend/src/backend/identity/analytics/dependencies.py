from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.analytics.managers import UserAnalyticsManager


async def get_user_analytics_manager(
        session: AsyncSession = Depends(get_db)
) -> UserAnalyticsManager:
    return UserAnalyticsManager(session)
