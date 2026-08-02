from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.notifications.dependencies import get_notification_preference_manager, \
    get_notification_preference_or_404
from src.backend.notifications.managers.preference import NotificationPreferenceManager
from src.backend.notifications.models import NotificationPreference
from src.backend.notifications.schemas import GetNotificationPreference, CreateNotificationPreference, \
    UpdateNotificationPreference

router = APIRouter(
    prefix="/notifications/preferences",
    tags=["notification_preferences"]
)

@cbv(router)
class NotificationPreferenceRouter:
    manager: NotificationPreferenceManager = Depends(get_notification_preference_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating notification preference",
        response_model=GetNotificationPreference
    )
    async def create_preference(
            self,
            request: CreateNotificationPreference
    ):
        result = await self.manager.create_preference(self.user, request)
        return result

    @router.put(
        "/mute",
        summary="muting all notifications for current user",
    )
    async def mute_all(self):
        await self.manager.mute_all(self.user)

    @router.put(
        "/unmute",
        summary="unmuting all notifications for current user",
    )
    async def unmute_all(self):
        await self.manager.unmute_all(self.user)

    @router.put(
        "/{preference_id}",
        summary="updating notification preference",
    )
    async def update_preference(
            self,
            request: UpdateNotificationPreference,
            preference: NotificationPreference = Depends(get_notification_preference_or_404)
    ):
        await self.manager.update_preference(self.user, preference, request)

    @router.delete(
        "/{preference_id}",
        summary="deleting notification preference",
    )
    async def delete_preference(
            self,
            preference: NotificationPreference = Depends(get_notification_preference_or_404)
    ):
        await self.manager.delete_preference(self.user, preference)

    @router.get(
        "/",
        summary="getting current user notification preferences",
        response_model=list[GetNotificationPreference]
    )
    async def get_user_preferences(self):
        result = await self.manager.get_user_preferences(self.user)
        return result

    @router.get(
        "/{preference_id}",
        summary="getting notification preference by id",
        response_model=GetNotificationPreference
    )
    async def get_preference_by_id(
            self,
            preference: NotificationPreference = Depends(get_notification_preference_or_404)
    ):
        return preference
