from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.administration.announcements.dependencies import get_announcement_manager
from src.backend.administration.announcements.managers import AnnouncementManager
from src.backend.administration.announcements.schemas import GetAnnouncement

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)

@cbv(router)
class AnnouncementPublicRouter:
    """CBV router for public read access to published announcements."""

    manager: AnnouncementManager = Depends(get_announcement_manager)

    @router.get(
        "/",
        summary="getting published announcements",
        response_model=list[GetAnnouncement]
    )
    async def get_published_announcements(self):
        """Lists all published announcements."""
        result = await self.manager.get_published_announcements()
        return result
