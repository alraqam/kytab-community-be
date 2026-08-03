from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.notifications.dependencies import get_notification_manager, get_notification_or_404
from src.backend.notifications.filters import NotificationFilter
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.models import Notification
from src.backend.notifications.schemas import GetNotification

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

@cbv(router)
class NotificationRouter:
    """CBV router for managing the current user's notifications: read, unread count, and deletion."""

    manager: NotificationManager = Depends(get_notification_manager)
    user: User = Depends(get_current_user)

    @router.put(
        "/read-all",
        summary="marking all notifications as read",
    )
    async def mark_all_as_read(self):
        """Marks all of the current user's notifications as read."""
        await self.manager.mark_all_as_read(self.user)

    @router.put(
        "/{notification_id}/read",
        summary="marking notification as read",
    )
    async def mark_as_read(
            self,
            notification: Notification = Depends(get_notification_or_404)
    ):
        """Marks a single notification as read."""
        await self.manager.mark_as_read(self.user, notification)

    @router.delete(
        "/{notification_id}",
        summary="deleting notification",
    )
    async def delete_notification(
            self,
            notification: Notification = Depends(get_notification_or_404)
    ):
        """Deletes a notification."""
        await self.manager.delete_notification(self.user, notification)

    @router.get(
        "/",
        summary="getting current user notifications",
        response_model=list[GetNotification]
    )
    async def get_user_notifications(
            self,
            filters: NotificationFilter = FilterDepends(NotificationFilter)
    ):
        """Lists the current user's notifications, optionally filtered."""
        result = await self.manager.get_user_notifications(self.user, filters)
        return result

    @router.get(
        "/unread-count",
        summary="getting unread notifications count",
    )
    async def get_unread_count(self) -> int:
        """Returns the current user's unread notification count."""
        result = await self.manager.get_unread_count(self.user)
        return result

    @router.get(
        "/{notification_id}",
        summary="getting notification by id",
        response_model=GetNotification
    )
    async def get_notification_by_id(
            self,
            notification: Notification = Depends(get_notification_or_404)
    ):
        """Fetches a single notification by ID."""
        return notification