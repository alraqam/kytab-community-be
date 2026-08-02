from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.library.reviews.dependencies import is_review_like_owner
from src.backend.library.reviews.exceptions import ReviewLikeNotFoundError, ReviewLikeAlreadyExists
from src.backend.library.reviews.models import Review, ReviewLike
from src.backend.library.reviews.repositories.like import ReviewLikeRepository
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory


class ReviewLikeManager:

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.like_repo = ReviewLikeRepository(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)

    async def create_like(
            self,
            user: User,
            review: Review,
    ) -> ReviewLike:
        try:
            response = await self.like_repo.create_like(
                user_id=user.id,
                review_id=review.id,
            )
            await self.session.commit()

            if review.user_id != user.id:
                owner = await self.user_manager.get_user_by_id(review.user_id)
                await self.notification_manager.notify(
                    owner,
                    category=NotificationCategory.general,
                    title=f"{user.username} liked your review",
                )
            return response
        except IntegrityError:
            await self.session.rollback()
            raise ReviewLikeAlreadyExists("Like for this review already exists")

    async def delete_like(
            self,
            user: User,
            like: ReviewLike,
    ) -> None:
        await is_review_like_owner(user, like)
        await self.like_repo.delete_like(
            like=like,
        )
        await self.session.commit()

    async def get_review_likes_count(
            self,
            review: Review,
    ) -> int:
        likes = await self.like_repo.get_review_likes(review_id=review.id)
        return len(likes)

    async def get_review_likes(
            self,
            review: Review,
    ) -> list[ReviewLike]:
        likes = await self.like_repo.get_review_likes(review_id=review.id)
        return likes

    async def get_like_by_id(
            self,
            like_id: int,
    ) -> ReviewLike:
        result = await self.like_repo.get_like_by_id(like_id=like_id)
        if not result:
            raise ReviewLikeNotFoundError("Like not found")
        return result
