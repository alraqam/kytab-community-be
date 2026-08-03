from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reviews.models import ReviewLike


@dataclass
class ReviewLikeRepository:
    """Data-access layer for review like persistence and queries."""

    session: AsyncSession

    async def create_like(
            self,
            user_id: int,
            review_id: int,
    ) -> ReviewLike:
        """Inserts a new like on a review.

        Args:
            user_id: ID of the user liking the review.
            review_id: ID of the review being liked.

        Returns:
            Newly created ReviewLike instance.
        """
        result = ReviewLike(
            user_id=user_id,
            review_id=review_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def delete_like(
            self,
            like: ReviewLike,
    ) -> None:
        """Deletes a review like.

        Args:
            like: ReviewLike instance to delete.
        """
        await self.session.delete(like)
        await self.session.flush()

    async def get_review_likes(
            self,
            review_id: int
    ) -> list[ReviewLike]:
        """Lists all likes on a review.

        Args:
            review_id: ID of the review to list likes for.

        Returns:
            List of matching ReviewLike instances.
        """
        stmt = select(ReviewLike).where(ReviewLike.review_id == review_id)
        result = await self.session.execute(stmt)
        likes = result.scalars().all()
        return likes

    async def get_like_by_id(
            self,
            like_id: int
    ) -> ReviewLike | None:
        """Fetches a single like by ID.

        Args:
            like_id: ID of the like to fetch.

        Returns:
            Matching ReviewLike instance, or None if not found.
        """
        stmt = select(ReviewLike).where(ReviewLike.id == like_id)
        result = await self.session.execute(stmt)
        likes = result.scalar_one_or_none()
        return likes