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
        for user in users:
            await self.notify(user, category, title, body, object_type, object_id, club_id)

    async def mark_as_read(
            self,
            user: User,
            notification: Notification,
    ) -> None:
        await is_notification_owner(user, notification)
        await self.notification_repo.mark_as_read(notification)
        await self.session.commit()

    async def mark_all_as_read(
            self,
            user: User,
    ) -> None:
        await self.notification_repo.mark_all_as_read(user.id)
        await self.session.commit()

    async def delete_notification(
            self,
            user: User,
            notification: Notification,
    ) -> None:
        await is_notification_owner(user, notification)
        await self.notification_repo.delete_notification(notification)
        await self.session.commit()

    async def get_user_notifications(
            self,
            user: User,
            filters: NotificationFilter | None = None,
    ) -> list[Notification]:
        result = await self.notification_repo.get_user_notifications(user.id, filters)
        return result

    async def get_unread_count(
            self,
            user: User,
    ) -> int:
        result = await self.notification_repo.get_unread_count(user.id)
        return result

    async def get_notification_by_id(
            self,
            notification_id: int,
    ) -> Notification:
        result = await self.notification_repo.get_notification_by_id(notification_id)
        if not result:
            raise NotificationNotFoundError("Notification not found")
        return result
