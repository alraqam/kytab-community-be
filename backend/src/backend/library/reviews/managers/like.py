from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.library.reviews.dependencies import is_review_like_owner
from src.backend.library.reviews.exceptions import ReviewLikeNotFoundError, ReviewLikeAlreadyExists
from src.backend.library.reviews.models import Review, ReviewLike
from src.backend.library.reviews.repositories.like import ReviewLikeRepository


class ReviewLikeManager:

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.like_repo = ReviewLikeRepository(session)

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
