from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.notifications.dependencies.notification import get_notification_preference_manager, \
    get_notification_preference_or_404
from src.backend.notifications.managers.preference import NotificationPreferenceManager
from src.backend.notifications.models.notification import NotificationPreference
from src.backend.notifications.schemas.notification import GetNotificationPreference, CreateNotificationPreference, \
    UpdateNotificationPreference
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/notifications/preferences",
    tags=["notification_preferences"]
)

@cbv(router)
class NotificationPreferenceRouter:
    """CBV router for managing the current user's notification delivery preferences."""

    manager: NotificationPreferenceManager = Depends(get_notification_preference_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating notification preference",
        response_model=GetNotificationPreference,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 404, 409),
    )
    async def create_preference(
            self,
            request: CreateNotificationPreference
    ):
        """Creates a notification preference for a category, optionally scoped to a club."""
        result = await self.manager.create_preference(self.user, request)
        return result

    @router.put(
        "/mute",
        summary="muting all notifications for current user",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401),
    )
    async def mute_all(self):
        """Mutes all of the current user's notification preferences."""
        await self.manager.mute_all(self.user)

    @router.put(
        "/unmute",
        summary="unmuting all notifications for current user",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401),
    )
    async def unmute_all(self):
        """Unmutes all of the current user's notification preferences."""
        await self.manager.unmute_all(self.user)

    @router.put(
        "/{preference_id}",
        summary="updating notification preference",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403),
    )
    async def update_preference(
            self,
            request: UpdateNotificationPreference,
            preference: NotificationPreference = Depends(get_notification_preference_or_404)
    ):
        """Updates a notification preference's channel settings."""
        await self.manager.update_preference(self.user, preference, request)

    @router.delete(
        "/{preference_id}",
        summary="deleting notification preference",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403),
    )
    async def delete_preference(
            self,
            preference: NotificationPreference = Depends(get_notification_preference_or_404)
    ):
        """Deletes a notification preference."""
        await self.manager.delete_preference(self.user, preference)

    @router.get(
        "/",
        summary="getting current user notification preferences",
        response_model=list[GetNotificationPreference],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_user_preferences(self):
        """Lists the current user's notification preferences."""
        result = await self.manager.get_user_preferences(self.user)
        return result

    @router.get(
        "/{preference_id}",
        summary="getting notification preference by id",
        response_model=GetNotificationPreference,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_preference_by_id(
            self,
            preference: NotificationPreference = Depends(get_notification_preference_or_404)
    ):
        """Fetches a single notification preference by ID."""
        return preference
