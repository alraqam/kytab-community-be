from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.auth.models import User
from src.backend.notifications.exceptions import IsNotNotificationOwnerError, IsNotNotificationPreferenceOwnerError
from src.backend.notifications.models import Notification, NotificationPreference

if TYPE_CHECKING:
    from src.backend.notifications.managers.notification import NotificationManager
    from src.backend.notifications.managers.preference import NotificationPreferenceManager


async def is_notification_owner(
        user: User,
        notification: Notification,
) -> None:
    if notification.user_id != user.id:
        raise IsNotNotificationOwnerError("Only notification owner can access and change their notification")
    return

async def is_notification_preference_owner(
        user: User,
        preference: NotificationPreference,
) -> None:
    if preference.user_id != user.id:
        raise IsNotNotificationPreferenceOwnerError("Only preference owner can access and change their preference")
    return

async def get_notification_preference_manager(
        session: AsyncSession = Depends(get_db)
) -> "NotificationPreferenceManager":
    from src.backend.notifications.managers.preference import NotificationPreferenceManager
    return NotificationPreferenceManager(session)

async def get_notification_preference_or_404(
        preference_id: int,
        manager: "NotificationPreferenceManager" = Depends(get_notification_preference_manager)
) -> NotificationPreference:
    return await manager.get_preference_by_id(preference_id)

async def get_notification_manager(
        session: AsyncSession = Depends(get_db)
) -> "NotificationManager":
    from src.backend.notifications.managers.notification import NotificationManager
    return NotificationManager(session)

async def get_notification_or_404(
        notification_id: int,
        manager: "NotificationManager" = Depends(get_notification_manager)
) -> Notification:
    return await manager.get_notification_by_id(notification_id)
