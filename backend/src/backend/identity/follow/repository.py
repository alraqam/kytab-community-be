from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.follow.models import Follow


@dataclass
class FollowRepository:
    """Data-access layer for follow relationship persistence and queries."""

    session: AsyncSession

    async def follow_user(
            self,
            follower_id: int,
            followed_id: int,
    ) -> Follow:
        """Inserts a new follow relationship.

        Args:
            follower_id: ID of the user who is following.
            followed_id: ID of the user being followed.

        Returns:
            Newly created Follow instance.
        """
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
        """Lists the follow relationships where the given user is followed.

        Args:
            user_id: ID of the user whose followers to list.

        Returns:
            List of matching Follow instances.
        """
        stmt = select(Follow).where(Follow.followed_id == user_id)
        result = await self.session.execute(stmt)
        follow = result.scalars().all()
        return follow

    async def get_user_followings(
            self,
            user_id: int
    ) -> list[Follow]:
        """Lists the follow relationships where the given user is the follower.

        Args:
            user_id: ID of the user whose followings to list.

        Returns:
            List of matching Follow instances.
        """
        stmt = select(Follow).where(Follow.follower_id == user_id)
        result = await self.session.execute(stmt)
        follow = result.scalars().all()
        return follow

    async def get_follow_by_id(
            self,
            follow_id: int
    ) -> Follow | None:
        """Fetches a single follow relationship by ID.

        Args:
            follow_id: ID of the follow relationship to fetch.

        Returns:
            Matching Follow instance, or None if not found.
        """
        stmt = select(Follow).where(Follow.id == follow_id)
        result = await self.session.execute(stmt)
        follow = result.scalar_one_or_none()
        return follow

    async def is_following_user(
            self,
            follower_id: int,
            followed_id: int,
    ) -> bool:
        """Checks whether a follow relationship exists between two users.

        Args:
            follower_id: ID of the potential follower.
            followed_id: ID of the potentially followed user.

        Returns:
            True if the follow relationship exists, False otherwise.
        """
        stmt = select(Follow).where(
            and_(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id,
            )
        )
        result = await self.session.execute(stmt)
        follows = result.scalar_one_or_none()
        return True if follows else False

    async def unfollow(
            self,
            follow: Follow
    ) -> None:
        """Deletes a follow relationship.

        Args:
            follow: Follow instance to delete.
        """
        await self.session.delete(follow)
        await self.session.flush()
