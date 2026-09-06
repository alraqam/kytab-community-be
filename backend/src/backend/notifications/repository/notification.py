from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.notifications.filters import NotificationFilter
from src.backend.notifications.models import Notification


@dataclass
class NotificationRepository:
    """Data-access layer for notification persistence and queries."""

    session: AsyncSession

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
        """Inserts a new unread notification.

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
        result = Notification(
            user_id=user_id,
            club_id=club_id,
            category=category,
            title=title,
            body=body,
            object_type=object_type,
            object_id=object_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def mark_as_read(
            self,
            notification: Notification,
    ) -> None:
        """Marks a single notification as read.

        Args:
            notification: Notification instance to update.
        """
        notification.is_read = True
        self.session.add(notification)
        await self.session.flush()

    async def mark_all_as_read(
            self,
            user_id: int,
    ) -> None:
        """Marks all unread notifications for a user as read.

        Args:
            user_id: ID of the user whose notifications to update.
        """
        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .values(is_read=True)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete_notification(
            self,
            notification: Notification,
    ) -> None:
        """Deletes a notification.

        Args:
            notification: Notification instance to delete.
        """
        await self.session.delete(notification)
        await self.session.flush()

    async def get_user_notifications(
            self,
            user_id: int,
            filters: NotificationFilter | None = None,
    ) -> list[Notification]:
        """Lists a user's notifications, optionally filtered and sorted.

        Args:
            user_id: ID of the user whose notifications to list.
            filters: NotificationFilter to apply, or None for no filtering.

        Returns:
            List of matching Notification instances.
        """
        stmt = select(Notification).where(Notification.user_id == user_id)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_unread_count(
            self,
            user_id: int,
    ) -> int:
        """Counts a user's unread notifications.

        Args:
            user_id: ID of the user whose unread notifications to count.

        Returns:
            Number of unread notifications.
        """
        stmt = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return len(lst)

    async def get_notifications_since(
            self,
            user_id: int,
            category: str,
            club_id: int | None,
            since: datetime,
    ) -> list[Notification]:
        """Lists a user's notifications for a category and club scope created after a timestamp.

        Args:
            user_id: ID of the user whose notifications to list.
            category: Notification category to match.
            club_id: Club ID to scope to, or None for the general (non-club) preference.
            since: Only notifications created after this timestamp are returned.

        Returns:
            List of matching Notification instances, oldest first.
        """
        stmt = (
            select(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.category == category,
                    Notification.club_id == club_id,
                    Notification.created_at > since,
                )
            )
            .order_by(Notification.created_at)
        )
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_notification_by_id(
            self,
            notification_id: int,
    ) -> Notification | None:
        """Fetches a single notification by ID.

        Args:
            notification_id: ID of the notification to fetch.

        Returns:
            Matching Notification instance, or None if not found.
        """
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        notification = result.scalar_one_or_none()
        return notification
