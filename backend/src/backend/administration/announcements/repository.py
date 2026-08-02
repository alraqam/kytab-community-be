from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.announcements.filters import AnnouncementFilter
from src.backend.administration.announcements.models import Announcement


@dataclass
class AnnouncementRepository:
    session: AsyncSession

    async def create_announcement(
            self,
            created_by_id: int,
            title: str,
            body: str,
    ) -> Announcement:
        result = Announcement(
            created_by_id=created_by_id,
            title=title,
            body=body,
            is_published=False,
            published_at=None,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_announcement(
            self,
            announcement: Announcement,
            title: str | None = None,
            body: str | None = None,
    ) -> None:
        updates = {
            "title": title,
            "body": body,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(announcement, field, value)
        await self.session.flush()

    async def update_published_status(
            self,
            announcement: Announcement,
            status: bool,
    ) -> None:
        announcement.is_published = status
        announcement.published_at = datetime.now() if status else None
        self.session.add(announcement)
        await self.session.flush()

    async def delete_announcement(
            self,
            announcement: Announcement,
    ) -> None:
        await self.session.delete(announcement)
        await self.session.flush()

    async def get_announcements(
            self,
            filters: AnnouncementFilter | None = None,
    ) -> list[Announcement]:
        stmt = select(Announcement)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_published_announcements(
            self,
    ) -> list[Announcement]:
        stmt = select(Announcement).where(Announcement.is_published == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_announcement_by_id(
            self,
            announcement_id: int,
    ) -> Announcement | None:
        stmt = select(Announcement).where(Announcement.id == announcement_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
