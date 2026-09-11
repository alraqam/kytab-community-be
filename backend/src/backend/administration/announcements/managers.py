from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.announcements.exceptions import AnnouncementNotFoundError
from src.backend.administration.announcements.filters import AnnouncementFilter
from src.backend.administration.announcements.models import Announcement
from src.backend.administration.announcements.repository import AnnouncementRepository
from src.backend.administration.announcements.schemas import CreateAnnouncement, UpdateAnnouncement
from src.backend.identity.auth.models import User


class AnnouncementManager:
    """Handles announcement business logic: creation, publishing, and retrieval."""

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
        """Creates a new announcement authored by the given user.

        Args:
            user: Admin user creating the announcement.
            request: CreateAnnouncement payload with title and body.

        Returns:
            Newly created Announcement instance.
        """
        result = await self.announcement_repo.create_announcement(
            created_by_id=user.id,
            title=request.title,
            body=request.body,
        )
        await self.session.commit()
        # created_by_username is a column_property computed via subquery, so it's never
        # populated on a freshly-inserted row; set it in-memory to avoid a lazy-load
        # attempt during response serialization (which fails outside an async context).
        result.created_by_username = user.username
        return result

    async def update_announcement(
            self,
            announcement: Announcement,
            request: UpdateAnnouncement,
    ) -> None:
        """Updates an announcement's title and/or body.

        Args:
            announcement: Announcement instance to update.
            request: UpdateAnnouncement payload with the fields to change.
        """
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
        """Marks an announcement as published and stamps the publish time.

        Args:
            announcement: Announcement instance to publish.
        """
        await self.announcement_repo.update_published_status(announcement, True)
        await self.session.commit()

    async def unpublish_announcement(
            self,
            announcement: Announcement,
    ) -> None:
        """Marks an announcement as unpublished and clears the publish time.

        Args:
            announcement: Announcement instance to unpublish.
        """
        await self.announcement_repo.update_published_status(announcement, False)
        await self.session.commit()

    async def delete_announcement(
            self,
            announcement: Announcement,
    ) -> None:
        """Permanently deletes an announcement.

        Args:
            announcement: Announcement instance to delete.
        """
        await self.announcement_repo.delete_announcement(announcement)
        await self.session.commit()

    async def get_announcements(
            self,
            filters: AnnouncementFilter,
    ) -> list[Announcement]:
        """Lists announcements matching the given filters.

        Args:
            filters: AnnouncementFilter with search, status, and ordering criteria.

        Returns:
            List of matching Announcement instances.
        """
        return await self.announcement_repo.get_announcements(filters)

    async def get_published_announcements(
            self,
    ) -> list[Announcement]:
        """Lists all published announcements.

        Returns:
            List of published Announcement instances.
        """
        return await self.announcement_repo.get_published_announcements()

    async def get_announcement_by_id(
            self,
            announcement_id: int,
    ) -> Announcement:
        """Fetches a single announcement by ID.

        Args:
            announcement_id: ID of the announcement to fetch.

        Returns:
            Matching Announcement instance.

        Raises:
            AnnouncementNotFoundError: When no announcement matches the ID.
        """
        result = await self.announcement_repo.get_announcement_by_id(announcement_id)
        if not result:
            raise AnnouncementNotFoundError("Announcement not found")
        return result
