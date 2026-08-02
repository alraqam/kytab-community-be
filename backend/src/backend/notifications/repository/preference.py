from dataclasses import dataclass

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.notifications.models import NotificationPreference


@dataclass
class NotificationPreferenceRepository:
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
        await self.session.delete(preference)
        await self.session.flush()

    async def mute_all(
            self,
            user_id: int,
    ) -> None:
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

    async def get_preference_by_id(
            self,
            preference_id: int,
    ) -> NotificationPreference | None:
        stmt = select(NotificationPreference).where(NotificationPreference.id == preference_id)
        result = await self.session.execute(stmt)
        preference = result.scalar_one_or_none()
        return preference
