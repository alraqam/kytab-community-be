from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.profile.models import Profile
from src.backend.identity.profile.schemas import ProfileVisibilityEnum


@dataclass
class ProfileRepository:
    session: AsyncSession

    async def create(
            self,
            user_id: int,
            fullname: str,
    ) -> Profile:
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
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()
        return profile

    async def update_avatar(
            self,
            profile: Profile,
            avatar: str
    ) -> None:
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
        profile.visibility = visibility
        self.session.add(profile)
        await self.session.flush()