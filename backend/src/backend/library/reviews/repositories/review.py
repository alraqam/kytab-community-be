from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reviews.filters import ReviewFilter
from src.backend.library.reviews.models import Review


@dataclass
class ReviewRepository:
    """Data-access layer for review persistence and queries."""

    session: AsyncSession

    async def create_review(
            self,
            user_id: int,
            work_id: int,
            contains_spoiler: bool,
            rating: float| None = None,
            text: str | None = None,
    ) -> Review:
        """Inserts a new review.

        Args:
            user_id: ID of the user creating the review.
            work_id: ID of the work being reviewed.
            contains_spoiler: Whether the review contains spoilers.
            rating: Optional rating for the work.
            text: Optional review text.

        Returns:
            Newly created Review instance.
        """
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
        """Updates the given fields of a review, skipping unset ones.

        Args:
            review: Review instance to update.
            rating: New rating, or None to leave unchanged.
            text: New text, or None to leave unchanged.
            contains_spoiler: New spoiler flag, or None to leave unchanged.
        """
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
        """Sets a review's edited flag.

        Args:
            review: Review instance to update.
            status: New value for the edited flag.
        """
        review.status = status
        self.session.add(review)
        await self.session.flush()

    async def delete_review(
            self,
            review: Review,
    ) -> None:
        """Deletes a review.

        Args:
            review: Review instance to delete.
        """
        await self.session.delete(review)
        await self.session.flush()

    async def get_work_reviews(
            self,
            work_id: int,
            filters: ReviewFilter | None = None,
    ) -> list[Review]:
        """Lists reviews for a work, optionally filtered and sorted.

        Args:
            work_id: ID of the work to list reviews for.
            filters: ReviewFilter to apply, or None for no filtering.

        Returns:
            List of matching Review instances.
        """
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
        """Fetches a user's review for a specific work, if any.

        Args:
            work_id: ID of the work.
            user_id: ID of the user.

        Returns:
            Matching Review instance, or None if the user has not reviewed the work.
        """
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
        """Lists all reviews written by a user.

        Args:
            user_id: ID of the user.

        Returns:
            List of the user's Review instances.
        """
        stmt = select(Review).where(Review.user_id == user_id)
        result = await self.session.execute(stmt)
        reviews = result.scalars().all()
        return reviews

    async def get_reviews_for_users(
            self,
            user_ids: list[int],
    ) -> list[Review]:
        """Lists all reviews written by any of the given users.

        Args:
            user_ids: IDs of the users whose reviews to list.

        Returns:
            List of matching Review instances.
        """
        stmt = select(Review).where(Review.user_id.in_(user_ids))
        result = await self.session.execute(stmt)
        reviews = result.scalars().all()
        return reviews

    async def get_review_by_id(
            self,
            review_id: int,
    ) -> Review | None:
        """Fetches a single review by ID.

        Args:
            review_id: ID of the review to fetch.

        Returns:
            Matching Review instance, or None if not found.
        """
        stmt = select(Review).where(Review.id == review_id)
        result = await self.session.execute(stmt)
        review = result.scalar_one_or_none()
        return review