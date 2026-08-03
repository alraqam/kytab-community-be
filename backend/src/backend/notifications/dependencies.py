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
    """Checks that a user owns the given notification.

    Args:
        user: User attempting the action.
        notification: Notification instance to check ownership of.

    Raises:
        IsNotNotificationOwnerError: When the user does not own the notification.
    """
    if notification.user_id != user.id:
        raise IsNotNotificationOwnerError("Only notification owner can access and change their notification")
    return

async def is_notification_preference_owner(
        user: User,
        preference: NotificationPreference,
) -> None:
    """Checks that a user owns the given notification preference.

    Args:
        user: User attempting the action.
        preference: NotificationPreference instance to check ownership of.

    Raises:
        IsNotNotificationPreferenceOwnerError: When the user does not own the preference.
    """
    if preference.user_id != user.id:
        raise IsNotNotificationPreferenceOwnerError("Only preference owner can access and change their preference")
    return

async def get_notification_preference_manager(
        session: AsyncSession = Depends(get_db)
) -> "NotificationPreferenceManager":
    """Builds a NotificationPreferenceManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        NotificationPreferenceManager instance.
    """
    from src.backend.notifications.managers.preference import NotificationPreferenceManager
    return NotificationPreferenceManager(session)

async def get_notification_preference_or_404(
        preference_id: int,
        manager: "NotificationPreferenceManager" = Depends(get_notification_preference_manager)
) -> NotificationPreference:
    """Resolves a notification preference by path parameter or raises if it doesn't exist.

    Args:
        preference_id: ID of the preference from the path.
        manager: NotificationPreferenceManager used to look up the preference.

    Returns:
        NotificationPreference instance.

    Raises:
        NotificationPreferenceNotFoundError: When no preference matches the ID.
    """
    return await manager.get_preference_by_id(preference_id)

async def get_notification_manager(
        session: AsyncSession = Depends(get_db)
) -> "NotificationManager":
    """Builds a NotificationManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        NotificationManager instance.
    """
    from src.backend.notifications.managers.notification import NotificationManager
    return NotificationManager(session)

async def get_notification_or_404(
        notification_id: int,
        manager: "NotificationManager" = Depends(get_notification_manager)
) -> Notification:
    """Resolves a notification by path parameter or raises if it doesn't exist.

    Args:
        notification_id: ID of the notification from the path.
        manager: NotificationManager used to look up the notification.

    Returns:
        Notification instance.

    Raises:
        NotificationNotFoundError: When no notification matches the ID.
    """
    return await manager.get_notification_by_id(notification_id)
