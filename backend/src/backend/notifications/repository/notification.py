from dataclasses import dataclass

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.notifications.filters import NotificationFilter
from src.backend.notifications.models import Notification


@dataclass
class NotificationRepository:
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
        notification.is_read = True
        self.session.add(notification)
        await self.session.flush()

    async def mark_all_as_read(
            self,
            user_id: int,
    ) -> None:
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
        await self.session.delete(notification)
        await self.session.flush()

    async def get_user_notifications(
            self,
            user_id: int,
            filters: NotificationFilter | None = None,
    ) -> list[Notification]:
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
        stmt = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return len(lst)

    async def get_notification_by_id(
            self,
            notification_id: int,
    ) -> Notification | None:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        notification = result.scalar_one_or_none()
        return notification
