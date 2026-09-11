from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.administration.announcements.dependencies import get_announcement_manager, get_announcement_or_404
from src.backend.administration.announcements.filters import AnnouncementFilter
from src.backend.administration.announcements.managers import AnnouncementManager
from src.backend.administration.announcements.models import Announcement
from src.backend.administration.announcements.schemas import CreateAnnouncement, UpdateAnnouncement, GetAnnouncement
from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.trust_safety.audit_log.decorators import audit_action
from src.backend.trust_safety.audit_log.schemas import AuditLogAction

router = APIRouter(
    prefix="/admin/announcements",
    tags=["admin"]
)

@cbv(router)
class AnnouncementAdminRouter:
    """CBV router for admin management of announcements: create, update, publish, and delete."""

    manager: AnnouncementManager = Depends(get_announcement_manager)
    user: User = Depends(is_admin)

    @router.post(
        "/",
        summary="creating announcement",
        response_model=GetAnnouncement
    )
    @audit_action(AuditLogAction.announcement_created, "announcement", id_from="result")
    async def create_announcement(
            self,
            request: CreateAnnouncement
    ):
        """Creates a new announcement."""
        result = await self.manager.create_announcement(self.user, request)
        return result

    @router.put(
        "/{announcement_id}",
        summary="updating announcement",
    )
    @audit_action(AuditLogAction.announcement_updated, "announcement", id_from="announcement")
    async def update_announcement(
            self,
            request: UpdateAnnouncement,
            announcement: Announcement = Depends(get_announcement_or_404),
    ):
        """Updates an announcement's title and/or body."""
        await self.manager.update_announcement(announcement, request)

    @router.put(
        "/{announcement_id}/publish",
        summary="publishing announcement",
    )
    @audit_action(AuditLogAction.announcement_published, "announcement", id_from="announcement")
    async def publish_announcement(
            self,
            announcement: Announcement = Depends(get_announcement_or_404),
    ):
        """Publishes an announcement."""
        await self.manager.publish_announcement(announcement)

    @router.put(
        "/{announcement_id}/unpublish",
        summary="unpublishing announcement",
    )
    @audit_action(AuditLogAction.announcement_unpublished, "announcement", id_from="announcement")
    async def unpublish_announcement(
            self,
            announcement: Announcement = Depends(get_announcement_or_404),
    ):
        """Unpublishes an announcement."""
        await self.manager.unpublish_announcement(announcement)

    @router.delete(
        "/{announcement_id}",
        summary="deleting announcement",
    )
    @audit_action(AuditLogAction.announcement_deleted, "announcement", id_from="announcement")
    async def delete_announcement(
            self,
            announcement: Announcement = Depends(get_announcement_or_404),
    ):
        """Deletes an announcement."""
        await self.manager.delete_announcement(announcement)

    @router.get(
        "/",
        summary="getting announcements",
        response_model=list[GetAnnouncement]
    )
    async def get_announcements(
            self,
            filters: AnnouncementFilter = FilterDepends(AnnouncementFilter)
    ):
        """Lists announcements, optionally filtered and sorted."""
        result = await self.manager.get_announcements(filters)
        return result

    @router.get(
        "/{announcement_id}",
        summary="getting announcement by id",
        response_model=GetAnnouncement
    )
    async def get_announcement_by_id(
            self,
            announcement: Announcement = Depends(get_announcement_or_404),
    ):
        """Fetches a single announcement by ID."""
        return announcement
