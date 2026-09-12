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
    """Handles follow business logic: following, unfollowing, and follower/following lookups."""

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
        """Creates a follow relationship from the given user to the requested user.

        Args:
            user: User who is following.
            request: CreateFollow payload with the ID of the user to follow.

        Returns:
            Newly created Follow instance.

        Raises:
            BlockedUserError: When the requesting user is blocked by the user to follow.
            UserAlreadyFollowingError: When the requesting user already follows that user.
        """
        result = await self.block_manager.is_blocked_user(request.followed_id, user.id)
        if result:
            raise BlockedUserError("You are blocked by user")

        try:
            result = await self.follow_repo.follow_user(
                follower_id=user.id,
                followed_id=request.followed_id,
            )
            await self.session.commit()
            return await self.follow_repo.get_follow_by_id(result.id)
        except IntegrityError:
            raise UserAlreadyFollowingError("Already following this user")

    async def unfollow(
            self,
            user: User,
            follow: Follow
    ) -> None:
        """Removes a follow relationship on behalf of its owner.

        Args:
            user: User requesting the unfollow.
            follow: Follow instance to remove.

        Raises:
            NotFollowOwnerError: When the requesting user does not own the follow relationship.
        """
        if user.id != follow.follower_id and user.id != follow.followed_id:
            raise NotFollowOwnerError("Only follow owners can unfollow")

        await self.follow_repo.unfollow(
            follow=follow
        )
        await self.session.commit()

    async def get_user_followers(
            self,
            user: User,
    ) -> list[Follow]:
        """Lists the users following the given user.

        Args:
            user: User whose followers to list.

        Returns:
            List of Follow instances where the given user is followed.
        """
        result = await self.follow_repo.get_user_followers(
            user_id=user.id,
        )
        return result

    async def get_user_followings(
            self,
            user: User,
    ) -> list[Follow]:
        """Lists the users the given user is following.

        Args:
            user: User whose followings to list.

        Returns:
            List of Follow instances where the given user is the follower.
        """
        result = await self.follow_repo.get_user_followings(
            user_id=user.id,
        )
        return result


    async def get_follow_by_id(
            self,
            follow_id: int
    ) -> Follow:
        """Fetches a single follow relationship by ID.

        Args:
            follow_id: ID of the follow relationship to fetch.

        Returns:
            Matching Follow instance.

        Raises:
            FollowNotFoundError: When no follow relationship matches the ID.
        """
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
    ) -> bool:
        """Checks whether one user follows another, raising if they do not.

        Args:
            follower_id: ID of the potential follower.
            followed_id: ID of the potentially followed user.

        Returns:
            True if the follow relationship exists.

        Raises:
            NotUserFollowerError: When the follow relationship does not exist.
        """
        result = await self.follow_repo.is_following_user(
            follower_id=follower_id,
            followed_id=followed_id,
        )
        if not result:
            raise NotUserFollowerError("Not user follower")
        return result