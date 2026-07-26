from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reviews.models import ReviewLike


@dataclass
class ReviewLikeRepository:
    session: AsyncSession

    async def create_like(
            self,
            user_id: int,
            review_id: int,
    ) -> ReviewLike:
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
        await self.session.delete(like)
        await self.session.flush()

    async def get_review_likes(
            self,
            review_id: int
    ) -> list[ReviewLike]:
        stmt = select(ReviewLike).where(ReviewLike.review_id == review_id)
        result = await self.session.execute(stmt)
        likes = result.scalars().all()
        return likes

    async def get_like_by_id(
            self,
            like_id: int
    ) -> ReviewLike | None:
        stmt = select(ReviewLike).where(ReviewLike.id == like_id)
        result = await self.session.execute(stmt)
        likes = result.scalar_one_or_none()
        return likes