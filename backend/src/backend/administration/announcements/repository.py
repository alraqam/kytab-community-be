from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.announcements.filters import AnnouncementFilter
from src.backend.administration.announcements.models import Announcement


@dataclass
class AnnouncementRepository:
    """Data-access layer for announcement persistence and queries."""

    session: AsyncSession

    async def create_announcement(
            self,
            created_by_id: int,
            title: str,
            body: str,
    ) -> Announcement:
        """Inserts a new unpublished announcement.

        Args:
            created_by_id: ID of the admin user creating the announcement.
            title: Announcement title.
            body: Announcement body text.

        Returns:
            Newly created Announcement instance.
        """
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
        """Updates the given fields of an announcement, skipping unset ones.

        Args:
            announcement: Announcement instance to update.
            title: New title, or None to leave unchanged.
            body: New body, or None to leave unchanged.
        """
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
        """Sets an announcement's published flag and publish timestamp.

        Args:
            announcement: Announcement instance to update.
            status: True to publish, False to unpublish.
        """
        announcement.is_published = status
        announcement.published_at = datetime.now() if status else None
        self.session.add(announcement)
        await self.session.flush()

    async def delete_announcement(
            self,
            announcement: Announcement,
    ) -> None:
        """Deletes an announcement.

        Args:
            announcement: Announcement instance to delete.
        """
        await self.session.delete(announcement)
        await self.session.flush()

    async def get_announcements(
            self,
            filters: AnnouncementFilter | None = None,
    ) -> list[Announcement]:
        """Lists announcements, optionally filtered and sorted.

        Args:
            filters: AnnouncementFilter to apply, or None for no filtering.

        Returns:
            List of matching Announcement instances.
        """
        stmt = select(Announcement)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_published_announcements(
            self,
    ) -> list[Announcement]:
        """Lists all published announcements.

        Returns:
            List of published Announcement instances.
        """
        stmt = select(Announcement).where(Announcement.is_published == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_announcement_by_id(
            self,
            announcement_id: int,
    ) -> Announcement | None:
        """Fetches a single announcement by ID.

        Args:
            announcement_id: ID of the announcement to fetch.

        Returns:
            Matching Announcement instance, or None if not found.
        """
        stmt = select(Announcement).where(Announcement.id == announcement_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
