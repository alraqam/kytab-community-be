from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.blocked_users.exceptions import BlockedUserError
from src.backend.identity.blocked_users.managers import BlockedUserManager
from src.backend.identity.follow.exceptions import UserAlreadyFollowingError, NotFollowOwnerError, FollowNotFoundError, \
    NotUserFollowerError
from src.backend.identity.follow.models import Follow
from src.backend.identity.follow.repository import FollowRepository
from src.backend.identity.follow.schemas import CreateFollow


class FollowManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.follow_repo = FollowRepository(session)
        self.block_manager = BlockedUserManager(session)


    async def follow_user(
            self,
            user: User,
            request: CreateFollow,
    ) -> Follow:
        result = await self.block_manager.is_blocked_user(request.followed_id, user.id)
        if result:
            raise BlockedUserError("You are blocked by user")

        try:
            result = await self.follow_repo.follow_user(
                follower_id=user.id,
                followed_id=request.followed_id,
            )
            await self.session.commit()
            return result
        except IntegrityError:
            raise UserAlreadyFollowingError("Already following this user")

    async def unfollow(
            self,
            user: User,
            follow: Follow
    ) -> None:
        if not (user.id != follow.follower_id or user.id != follow.followed_id):
            raise NotFollowOwnerError("Only follow owners can unfollow")

        await self.follow_repo.unfollow(
            follow=follow
        )
        await self.session.commit()

    async def get_user_followers(
            self,
            user: User,
    ) -> list[Follow]:
        result = await self.follow_repo.get_user_followers(
            user_id=user.id,
        )
        return result

    async def get_user_followings(
            self,
            user: User,
    ) -> list[Follow]:
        result = await self.follow_repo.get_user_followings(
            user_id=user.id,
        )
        return result


    async def get_follow_by_id(
            self,
            follow_id: int
    ) -> Follow:
        result = await self.follow_repo.get_follow_by_id(
            follow_id=follow_id,
        )
        if not result:
            raise FollowNotFoundError("Following not found")
        return result

    async def is_following_user(
            self,
            follower_id: int,
            followed_id: int,
    ) -> Follow:
        result = await self.follow_repo.is_following_user(
            follower_id=follower_id,
            followed_id=followed_id,
        )
        if not result:
            raise NotUserFollowerError("Not user follower")
        return result