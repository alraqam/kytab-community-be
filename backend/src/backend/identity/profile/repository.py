from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.profile.models import Profile
from src.backend.identity.profile.schemas import ProfileVisibilityEnum


@dataclass
class ProfileRepository:
    """Data-access layer for profile persistence and queries."""

    session: AsyncSession

    async def create(
            self,
            user_id: int,
            fullname: str,
    ) -> Profile:
        """Inserts a new profile with public visibility.

        Args:
            user_id: ID of the user the profile belongs to.
            fullname: Full name to store on the profile.

        Returns:
            Newly created Profile instance.
        """
        result = Profile(
            user_id=user_id,
            fullname=fullname,
            visibility=ProfileVisibilityEnum.public
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_profile_by_user(
            self,
            user_id: int
    ) -> Profile | None:
        """Fetches the profile belonging to the given user ID.

        Args:
            user_id: ID of the user whose profile to fetch.

        Returns:
            Matching Profile instance, or None if not found.
        """
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()
        return profile

    async def update_avatar(
            self,
            profile: Profile,
            avatar: str
    ) -> None:
        """Sets a profile's avatar URL.

        Args:
            profile: Profile instance to update.
            avatar: New avatar URL.
        """
        profile.avatar = avatar
        self.session.add(profile)
        await self.session.flush()

    async def update_profile(
            self,
            profile: Profile,
            fullname: str | None,
            bio: str | None,
            favorite_genres: list | None,
            links: list | None,
    ) -> None:
        """Updates the given fields of a profile, skipping unset ones.

        Args:
            profile: Profile instance to update.
            fullname: New full name, or None to leave unchanged.
            bio: New bio text, or None to leave unchanged.
            favorite_genres: New list of favorite genres, or None to leave unchanged.
            links: New list of links, or None to leave unchanged.
        """
        updates = {
            "fullname": fullname,
            "bio": bio,
            "favorite_genres": favorite_genres,
            "links": links,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(profile, field, value)
        await self.session.flush()

    async def update_visibility(
            self,
            profile: Profile,
            visibility: str
    ):
        """Sets a profile's visibility setting.

        Args:
            profile: Profile instance to update.
            visibility: New visibility value.
        """
        profile.visibility = visibility
        self.session.add(profile)
        await self.session.flush()