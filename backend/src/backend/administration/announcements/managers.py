from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.announcements.exceptions import AnnouncementNotFoundError
from src.backend.administration.announcements.filters import AnnouncementFilter
from src.backend.administration.announcements.models import Announcement
from src.backend.administration.announcements.repository import AnnouncementRepository
from src.backend.administration.announcements.schemas import CreateAnnouncement, UpdateAnnouncement
from src.backend.identity.auth.models import User


class AnnouncementManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.announcement_repo = AnnouncementRepository(session)

    async def create_announcement(
            self,
            user: User,
            request: CreateAnnouncement,
    ) -> Announcement:
        result = await self.announcement_repo.create_announcement(
            created_by_id=user.id,
            title=request.title,
            body=request.body,
        )
        await self.session.commit()
        return result

    async def update_announcement(
            self,
            announcement: Announcement,
            request: UpdateAnnouncement,
    ) -> None:
        await self.announcement_repo.update_announcement(
            announcement=announcement,
            title=request.title,
            body=request.body,
        )
        await self.session.commit()

    async def publish_announcement(
            self,
            announcement: Announcement,
    ) -> None:
        await self.announcement_repo.update_published_status(announcement, True)
        await self.session.commit()

    async def unpublish_announcement(
            self,
            announcement: Announcement,
    ) -> None:
        await self.announcement_repo.update_published_status(announcement, False)
        await self.session.commit()

    async def delete_announcement(
            self,
            announcement: Announcement,
    ) -> None:
        await self.announcement_repo.delete_announcement(announcement)
        await self.session.commit()

    async def get_announcements(
            self,
            filters: AnnouncementFilter,
    ) -> list[Announcement]:
        return await self.announcement_repo.get_announcements(filters)

    async def get_published_announcements(
            self,
    ) -> list[Announcement]:
        return await self.announcement_repo.get_published_announcements()

    async def get_announcement_by_id(
            self,
            announcement_id: int,
    ) -> Announcement:
        result = await self.announcement_repo.get_announcement_by_id(announcement_id)
        if not result:
            raise AnnouncementNotFoundError("Announcement not found")
        return result
