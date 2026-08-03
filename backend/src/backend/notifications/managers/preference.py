from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.managers import ClubManager
from src.backend.identity.auth.models import User
from src.backend.notifications.dependencies import is_notification_preference_owner
from src.backend.notifications.exceptions import NotificationPreferenceNotFoundError, \
    NotificationPreferenceAlreadyExistsError
from src.backend.notifications.models import NotificationPreference
from src.backend.notifications.repository.preference import NotificationPreferenceRepository
from src.backend.notifications.schemas import CreateNotificationPreference, UpdateNotificationPreference


class NotificationPreferenceManager:
    """Handles notification preference business logic: creation, updates, and muting."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.preference_repo = NotificationPreferenceRepository(session)
        self.club_manager = ClubManager(self.session)

    async def create_preference(
            self,
            user: User,
            request: CreateNotificationPreference,
    ) -> NotificationPreference:
        """Creates a notification preference for a user, optionally scoped to a club.

        Args:
            user: User the preference belongs to.
            request: CreateNotificationPreference payload with category, club, and channel settings.

        Returns:
            Newly created NotificationPreference instance.

        Raises:
            ClubNotFoundError: When request.club_id is set but no matching club exists.
            NotificationPreferenceAlreadyExistsError: When a preference for this category and club already exists.
        """
        if request.club_id:
            await self.club_manager.get_club_by_id(request.club_id)
        try:
            result = await self.preference_repo.create_preference(
                user_id=user.id,
                category=request.category,
                club_id=request.club_id,
                in_app_enabled=request.in_app_enabled,
                email_enabled=request.email_enabled,
                push_enabled=request.push_enabled,
                digest_frequency=request.digest_frequency,
            )
            await self.session.commit()
            return result
        except IntegrityError:
            await self.session.rollback()
            raise NotificationPreferenceAlreadyExistsError("Preference for this category and club already exists")

    async def update_preference(
            self,
            user: User,
            preference: NotificationPreference,
            request: UpdateNotificationPreference,
    ) -> None:
        """Updates a notification preference's channel settings.

        Args:
            user: User performing the action; must own the preference.
            preference: NotificationPreference instance to update.
            request: UpdateNotificationPreference payload with the fields to change.

        Raises:
            IsNotNotificationPreferenceOwnerError: When the user does not own the preference.
        """
        await is_notification_preference_owner(user, preference)
        await self.preference_repo.update_preference(
            preference=preference,
            in_app_enabled=request.in_app_enabled,
            email_enabled=request.email_enabled,
            push_enabled=request.push_enabled,
            digest_frequency=request.digest_frequency,
        )
        await self.session.commit()

    async def delete_preference(
            self,
            user: User,
            preference: NotificationPreference,
    ) -> None:
        """Deletes a notification preference.

        Args:
            user: User performing the action; must own the preference.
            preference: NotificationPreference instance to delete.

        Raises:
            IsNotNotificationPreferenceOwnerError: When the user does not own the preference.
        """
        await is_notification_preference_owner(user, preference)
        await self.preference_repo.delete_preference(preference)
        await self.session.commit()

    async def mute_all(
            self,
            user: User,
    ) -> None:
        """Mutes all of a user's notification preferences.

        Args:
            user: User whose preferences should be muted.
        """
        await self.preference_repo.mute_all(user.id)
        await self.session.commit()

    async def unmute_all(
            self,
            user: User,
    ) -> None:
        """Unmutes all of a user's notification preferences.

        Args:
            user: User whose preferences should be unmuted.
        """
        await self.preference_repo.unmute_all(user.id)
        await self.session.commit()

    async def get_user_preferences(
            self,
            user: User,
    ) -> list[NotificationPreference]:
        """Lists all notification preferences belonging to a user.

        Args:
            user: User whose preferences to list.

        Returns:
            List of NotificationPreference instances.
        """
        result = await self.preference_repo.get_user_preferences(user.id)
        return result

    async def get_preference(
            self,
            user_id: int,
            category: str,
            club_id: int | None = None,
    ) -> NotificationPreference | None:
        """Fetches a user's preference for a category, optionally scoped to a club.

        Args:
            user_id: ID of the user whose preference to look up.
            category: Notification category.
            club_id: Optional club ID to scope the lookup to.

        Returns:
            Matching NotificationPreference, or None if not set.
        """
        result = await self.preference_repo.get_preference(user_id, category, club_id)
        return result

    async def get_preference_by_id(
            self,
            preference_id: int,
    ) -> NotificationPreference:
        """Fetches a single notification preference by ID.

        Args:
            preference_id: ID of the preference to fetch.

        Returns:
            Matching NotificationPreference instance.

        Raises:
            NotificationPreferenceNotFoundError: When no preference matches the ID.
        """
        result = await self.preference_repo.get_preference_by_id(preference_id)
        if not result:
            raise NotificationPreferenceNotFoundError("Preference not found")
        return result
