from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reviews.filters import ReviewFilter
from src.backend.library.reviews.models import Review


@dataclass
class ReviewRepository:
    session: AsyncSession

    async def create_review(
            self,
            user_id: int,
            work_id: int,
            contains_spoiler: bool,
            rating: float| None = None,
            text: str | None = None,
    ) -> Review:
        result = Review(
            user_id=user_id,
            work_id=work_id,
            rating=rating,
            text=text,
            contains_spoiler=contains_spoiler,
        )
        self.session.add(result)
        await self.session.flush()
        return result


    async def update_review(
            self,
            review: Review,
            rating: float| None,
            text: str| None,
            contains_spoiler: bool| None,
    ) -> None:
        updates = {
            "rating": rating,
            "text": text,
            "contains_spoiler": contains_spoiler,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(review, field, value)
        await self.session.flush()

    async def update_is_edited(
            self,
            review: Review,
            status: bool,
    ) -> None:
        review.status = status
        self.session.add(review)
        await self.session.flush()

    async def delete_review(
            self,
            review: Review,
    ) -> None:
        await self.session.delete(review)
        await self.session.flush()

    async def get_work_reviews(
            self,
            work_id: int,
            filters: ReviewFilter | None = None,
    ) -> list[Review]:
        stmt = select(Review).where(Review.work_id == work_id)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_user_review_for_work(
            self,
            work_id: int,
            user_id: int,
    ) -> Review | None:
        stmt = select(Review).where(
            and_(
                Review.work_id == work_id,
                Review.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        review = result.scalar_one_or_none()
        return review

    async def get_user_reviews(
            self,
            user_id: int,
    ) -> list[Review]:
        stmt = select(Review).where(Review.user_id == user_id)
        result = await self.session.execute(stmt)
        reviews = result.scalars().all()
        return reviews

    async def get_review_by_id(
            self,
            review_id: int,
    ) -> Review | None:
        stmt = select(Review).where(Review.id == review_id)
        result = await self.session.execute(stmt)
        review = result.scalar_one_or_none()
        return review