from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.announcements.managers import AnnouncementManager
from src.backend.administration.announcements.models import Announcement
from src.backend.core.dependencies import get_db


async def get_announcement_manager(
        session: AsyncSession = Depends(get_db)
) -> AnnouncementManager:
    """Builds an AnnouncementManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        AnnouncementManager instance.
    """
    return AnnouncementManager(session)

async def get_announcement_or_404(
        announcement_id: int,
        manager: AnnouncementManager = Depends(get_announcement_manager)
) -> Announcement:
    """Resolves an announcement by path parameter or raises if it doesn't exist.

    Args:
        announcement_id: ID of the announcement from the path.
        manager: AnnouncementManager used to look up the announcement.

    Returns:
        Announcement instance.

    Raises:
        AnnouncementNotFoundError: When no announcement matches the ID.
    """
    return await manager.get_announcement_by_id(announcement_id)
