from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.follow.models import Follow


@dataclass
class FollowRepository:
    session: AsyncSession

    async def follow_user(
            self,
            follower_id: int,
            followed_id: int,
    ) -> Follow:
        result = Follow(
            follower_id=follower_id,
            followed_id=followed_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_user_followers(
            self,
            user_id: int
    ) -> list[Follow]:
        stmt = select(Follow).where(Follow.followed_id == user_id)
        result = await self.session.execute(stmt)
        follow = result.scalars().all()
        return follow

    async def get_user_followings(
            self,
            user_id: int
    ) -> list[Follow]:
        stmt = select(Follow).where(Follow.follower_id == user_id)
        result = await self.session.execute(stmt)
        follow = result.scalars().all()
        return follow

    async def get_follow_by_id(
            self,
            follow_id: int
    ) -> Follow | None:
        stmt = select(Follow).where(Follow.id == follow_id)
        result = await self.session.execute(stmt)
        follow = result.scalar_one_or_none()
        return follow

    async def is_following_user(
            self,
            follower_id: int,
            followed_id: int,
    ) -> Follow | None:
        stmt = select(Follow).where(
            and_(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id,
            )
        )
        result = await self.session.execute(stmt)
        follows = result.scalar_one_or_none()
        return follows

    async def unfollow(
            self,
            follow: Follow
    ) -> None:
        await self.session.delete(follow)
        await self.session.flush()
