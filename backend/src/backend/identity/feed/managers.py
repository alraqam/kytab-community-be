from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.schemas import PageRequest, PageResult
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.identity.auth.models import User
from src.backend.identity.blocked_users.repository import BlockedUsersRepository
from src.backend.identity.feed.schemas import FeedItem, FeedItemType
from src.backend.identity.follow.repository import FollowRepository
from src.backend.identity.profile.repository import ProfileRepository
from src.backend.identity.profile.schemas import ProfileVisibilityEnum
from src.backend.library.reviews.repositories.review import ReviewRepository


class FeedManager:
    """Builds a user's home feed by combining followed users' reviews and club memberships."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.follow_repo = FollowRepository(session)
        self.blocked_repo = BlockedUsersRepository(session)
        self.profile_repo = ProfileRepository(session)
        self.membership_repo = ClubMembershipRepository(session)
        self.review_repo = ReviewRepository(session)

    async def get_visible_followed_ids(
            self,
            user: User,
    ) -> list[int]:
        """Lists the IDs of followed users whose activity may appear in the feed.

        Excludes users who have blocked the requesting user and users with a private profile.

        Args:
            user: User whose followings are being resolved.

        Returns:
            List of followed user IDs visible to the given user.
        """
        followings = await self.follow_repo.get_user_followings(user.id)

        result = []
        for following in followings:
            if await self.blocked_repo.is_blocked_user(following.followed_id, user.id):
                continue
            profile = await self.profile_repo.get_profile_by_user(following.followed_id)
            if profile and profile.visibility == ProfileVisibilityEnum.private:
                continue
            result.append(following.followed_id)
        return result

    async def get_home_feed(
            self,
            user: User,
            page_request: PageRequest,
    ) -> PageResult[FeedItem]:
        """Builds the current user's home feed: followed users' reviews and club memberships.

        Args:
            user: User the feed is being built for.
            page_request: Pagination parameters.

        Returns:
            PageResult of FeedItem, sorted by recency.
        """
        followed_ids = await self.get_visible_followed_ids(user)

        reviews = await self.review_repo.get_reviews_for_users(followed_ids) if followed_ids else []

        followed_memberships = (
            await self.membership_repo.get_memberships_for_users(followed_ids) if followed_ids else []
        )

        items = [
            FeedItem(
                type=FeedItemType.review,
                created_at=review.created_at,
                actor_id=review.user_id,
                actor_username=review.username,
                review_id=review.id,
                work_id=review.work_id,
                work_title=review.work_title,
                rating=review.rating,
                body=review.text,
            )
            for review in reviews
        ]
        items += [
            FeedItem(
                type=FeedItemType.club,
                created_at=membership.created_at,
                actor_id=membership.user_id,
                actor_username=membership.username,
                club_id=membership.club_id,
                club_name=membership.club_name,
            )
            for membership in followed_memberships
        ]

        items.sort(key=lambda item: item.created_at, reverse=True)

        total_items = len(items)
        page_items = items[page_request.offset:page_request.offset + page_request.limit]

        return PageResult(
            items=page_items,
            page=page_request.page,
            size=page_request.size,
            total_items=total_items,
        )
