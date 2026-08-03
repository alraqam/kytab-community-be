from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.analytics.managers import UserAnalyticsManager


async def get_user_analytics_manager(
        session: AsyncSession = Depends(get_db)
) -> UserAnalyticsManager:
    """Provides a UserAnalyticsManager bound to the request-scoped database session.

    Args:
        session: Database session injected via dependency.

    Returns:
        UserAnalyticsManager instance for the current request.
    """
    return UserAnalyticsManager(session)
