from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.feed.managers import FeedManager


async def get_feed_manager(
        session: AsyncSession = Depends(get_db)
) -> FeedManager:
    """Builds a FeedManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        FeedManager instance.
    """
    return FeedManager(session)
