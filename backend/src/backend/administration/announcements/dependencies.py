from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.announcements.managers import AnnouncementManager
from src.backend.administration.announcements.models import Announcement
from src.backend.core.dependencies import get_db


async def get_announcement_manager(
        session: AsyncSession = Depends(get_db)
) -> AnnouncementManager:
    return AnnouncementManager(session)

async def get_announcement_or_404(
        announcement_id: int,
        manager: AnnouncementManager = Depends(get_announcement_manager)
) -> Announcement:
    return await manager.get_announcement_by_id(announcement_id)
