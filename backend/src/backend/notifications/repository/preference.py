from dataclasses import dataclass

from datetime import datetime

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.notifications.models import NotificationPreference


@dataclass
class NotificationPreferenceRepository:
    """Data-access layer for notification preference persistence and queries."""

    session: AsyncSession

    async def create_preference(
            self,
            user_id: int,
            category: str,
            club_id: int | None,
            in_app_enabled: bool,
            email_enabled: bool,
            push_enabled: bool,
            digest_frequency: str,
    ) -> NotificationPreference:
        """Inserts a new notification preference.

        Args:
            user_id: ID of the user the preference belongs to.
            category: Notification category.
            club_id: Optional club ID to scope the preference to.
            in_app_enabled: Whether in-app delivery is enabled.
            email_enabled: Whether email delivery is enabled.
            push_enabled: Whether push delivery is enabled.
            digest_frequency: How often a digest should be sent.

        Returns:
            Newly created NotificationPreference instance.
        """
        result = NotificationPreference(
            user_id=user_id,
            club_id=club_id,
            category=category,
            in_app_enabled=in_app_enabled,
            email_enabled=email_enabled,
            push_enabled=push_enabled,
            digest_frequency=digest_frequency,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_preference(
            self,
            preference: NotificationPreference,
            in_app_enabled: bool | None,
            email_enabled: bool | None,
            push_enabled: bool | None,
            digest_frequency: str | None,
    ) -> None:
        """Updates the given fields of a preference, skipping unset ones.

        Args:
            preference: NotificationPreference instance to update.
            in_app_enabled: New in-app delivery setting, or None to leave unchanged.
            email_enabled: New email delivery setting, or None to leave unchanged.
            push_enabled: New push delivery setting, or None to leave unchanged.
            digest_frequency: New digest frequency, or None to leave unchanged.
        """
        updates = {
            "in_app_enabled": in_app_enabled,
            "email_enabled": email_enabled,
            "push_enabled": push_enabled,
            "digest_frequency": digest_frequency,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(preference, field, value)
        await self.session.flush()

    async def delete_preference(
            self,
            preference: NotificationPreference,
    ) -> None:
        """Deletes a notification preference.

        Args:
            preference: NotificationPreference instance to delete.
        """
        await self.session.delete(preference)
        await self.session.flush()

    async def mute_all(
            self,
            user_id: int,
    ) -> None:
        """Mutes all notification preferences for a user.

        Args:
            user_id: ID of the user whose preferences to mute.
        """
        stmt = (
            update(NotificationPreference)
            .where(NotificationPreference.user_id == user_id)
            .values(is_muted=True)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def unmute_all(
            self,
            user_id: int,
    ) -> None:
        """Unmutes all notification preferences for a user.

        Args:
            user_id: ID of the user whose preferences to unmute.
        """
        stmt = (
            update(NotificationPreference)
            .where(NotificationPreference.user_id == user_id)
            .values(is_muted=False)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_user_preferences(
            self,
            user_id: int,
    ) -> list[NotificationPreference]:
        """Lists all notification preferences belonging to a user.

        Args:
            user_id: ID of the user whose preferences to list.

        Returns:
            List of NotificationPreference instances.
        """
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_preference(
            self,
            user_id: int,
            category: str,
            club_id: int | None,
    ) -> NotificationPreference | None:
        """Fetches a preference matching the user, category, and club scope.

        Args:
            user_id: ID of the user whose preference to look up.
            category: Notification category.
            club_id: Club ID to scope the lookup to, or None for the general preference.

        Returns:
            Matching NotificationPreference, or None if not found.
        """
        stmt = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.category == category,
                NotificationPreference.club_id == club_id,
            )
        )
        result = await self.session.execute(stmt)
        preference = result.scalar_one_or_none()
        return preference

    async def get_by_digest_frequency(
            self,
            digest_frequency: str,
    ) -> list[NotificationPreference]:
        """Lists all non-muted preferences with a given digest frequency.

        Args:
            digest_frequency: Digest frequency to match ("daily" or "weekly").

        Returns:
            List of matching NotificationPreference instances.
        """
        stmt = select(NotificationPreference).where(
            and_(
                NotificationPreference.digest_frequency == digest_frequency,
                NotificationPreference.is_muted == False,
            )
        )
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def update_last_digest_sent_at(
            self,
            preference: NotificationPreference,
            when: datetime,
    ) -> None:
        """Records when a digest was last sent for a preference.

        Args:
            preference: NotificationPreference instance to update.
            when: Timestamp of the digest send.
        """
        preference.last_digest_sent_at = when
        await self.session.flush()

    async def get_preference_by_id(
            self,
            preference_id: int,
    ) -> NotificationPreference | None:
        """Fetches a single notification preference by ID.

        Args:
            preference_id: ID of the preference to fetch.

        Returns:
            Matching NotificationPreference instance, or None if not found.
        """
        stmt = select(NotificationPreference).where(NotificationPreference.id == preference_id)
        result = await self.session.execute(stmt)
        preference = result.scalar_one_or_none()
        return preference
