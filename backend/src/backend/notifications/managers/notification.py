from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.notifications.dependencies import is_notification_owner
from src.backend.notifications.email import send_notification_email
from src.backend.notifications.exceptions import NotificationNotFoundError
from src.backend.notifications.filters import NotificationFilter
from src.backend.notifications.managers.preference import NotificationPreferenceManager
from src.backend.notifications.models import Notification, NotificationPreference
from src.backend.notifications.repository.notification import NotificationRepository


class NotificationManager:
    """Handles notification business logic: creation, delivery preferences, and read/delete state."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.notification_repo = NotificationRepository(session)
        self.preference_manager = NotificationPreferenceManager(session)

    async def create_notification(
            self,
            user_id: int,
            category: str,
            title: str,
            body: str | None = None,
            object_type: str | None = None,
            object_id: int | None = None,
            club_id: int | None = None,
    ) -> Notification:
        """Creates a notification row for a user.

        Args:
            user_id: ID of the user the notification is for.
            category: Notification category.
            title: Notification title.
            body: Optional notification body.
            object_type: Optional type of the entity the notification references.
            object_id: Optional ID of the entity the notification references.
            club_id: Optional ID of the club the notification is scoped to.

        Returns:
            Newly created Notification instance.
        """
        result = await self.notification_repo.create_notification(
            user_id=user_id,
            category=category,
            title=title,
            body=body,
            object_type=object_type,
            object_id=object_id,
            club_id=club_id,
        )
        await self.session.commit()
        return result

    async def get_effective_preference(
            self,
            user_id: int,
            category: str,
            club_id: int | None = None,
    ) -> NotificationPreference | None:
        """Resolves the preference that governs a notification, preferring a club-scoped one over the general one.

        Args:
            user_id: ID of the user whose preference to look up.
            category: Notification category.
            club_id: Optional club ID to check for a club-scoped preference first.

        Returns:
            Matching NotificationPreference, or None if the user has no preference set for the category.
        """
        if club_id is not None:
            preference = await self.preference_manager.get_preference(user_id, category, club_id)
            if preference:
                return preference
        return await self.preference_manager.get_preference(user_id, category, None)

    async def notify(
            self,
            user: User,
            category: str,
            title: str,
            body: str | None = None,
            object_type: str | None = None,
            object_id: int | None = None,
            club_id: int | None = None,
    ) -> Notification | None:
        """Notifies a single user according to their effective preference: in-app row and/or email.

        Args:
            user: User to notify.
            category: Notification category.
            title: Notification title.
            body: Optional notification body.
            object_type: Optional type of the entity the notification references.
            object_id: Optional ID of the entity the notification references.
            club_id: Optional ID of the club the notification is scoped to.

        Returns:
            Created Notification if an in-app notification was recorded, otherwise None.
        """
        preference = await self.get_effective_preference(user.id, category, club_id)

        notification = None
        if preference is None or (preference.in_app_enabled and not preference.is_muted):
            notification = await self.create_notification(
                user_id=user.id,
                category=category,
                title=title,
                body=body,
                object_type=object_type,
                object_id=object_id,
                club_id=club_id,
            )

        if preference is not None and preference.email_enabled and not preference.is_muted:
            send_notification_email.delay(user.email, title, body)

        return notification

    async def notify_many(
            self,
            users: list[User],
            category: str,
            title: str,
            body: str | None = None,
            object_type: str | None = None,
            object_id: int | None = None,
            club_id: int | None = None,
    ) -> None:
        """Notifies multiple users, applying each user's own preference.

        Args:
            users: Users to notify.
            category: Notification category.
            title: Notification title.
            body: Optional notification body.
            object_type: Optional type of the entity the notification references.
            object_id: Optional ID of the entity the notification references.
            club_id: Optional ID of the club the notification is scoped to.
        """
        for user in users:
            await self.notify(user, category, title, body, object_type, object_id, club_id)

    async def mark_as_read(
            self,
            user: User,
            notification: Notification,
    ) -> None:
        """Marks a single notification as read.

        Args:
            user: User performing the action; must own the notification.
            notification: Notification instance to mark as read.

        Raises:
            IsNotNotificationOwnerError: When the user does not own the notification.
        """
        await is_notification_owner(user, notification)
        await self.notification_repo.mark_as_read(notification)
        await self.session.commit()

    async def mark_all_as_read(
            self,
            user: User,
    ) -> None:
        """Marks all of a user's unread notifications as read.

        Args:
            user: User whose notifications should be marked as read.
        """
        await self.notification_repo.mark_all_as_read(user.id)
        await self.session.commit()

    async def delete_notification(
            self,
            user: User,
            notification: Notification,
    ) -> None:
        """Deletes a notification.

        Args:
            user: User performing the action; must own the notification.
            notification: Notification instance to delete.

        Raises:
            IsNotNotificationOwnerError: When the user does not own the notification.
        """
        await is_notification_owner(user, notification)
        await self.notification_repo.delete_notification(notification)
        await self.session.commit()

    async def get_user_notifications(
            self,
            user: User,
            filters: NotificationFilter | None = None,
    ) -> list[Notification]:
        """Lists a user's notifications, optionally filtered.

        Args:
            user: User whose notifications to list.
            filters: NotificationFilter to apply, or None for no filtering.

        Returns:
            List of matching Notification instances.
        """
        result = await self.notification_repo.get_user_notifications(user.id, filters)
        return result

    async def get_unread_count(
            self,
            user: User,
    ) -> int:
        """Counts a user's unread notifications.

        Args:
            user: User whose unread notifications to count.

        Returns:
            Number of unread notifications.
        """
        result = await self.notification_repo.get_unread_count(user.id)
        return result

    async def get_notification_by_id(
            self,
            notification_id: int,
    ) -> Notification:
        """Fetches a single notification by ID.

        Args:
            notification_id: ID of the notification to fetch.

        Returns:
            Matching Notification instance.

        Raises:
            NotificationNotFoundError: When no notification matches the ID.
        """
        result = await self.notification_repo.get_notification_by_id(notification_id)
        if not result:
            raise NotificationNotFoundError("Notification not found")
        return result
