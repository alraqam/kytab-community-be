from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.catalog.books.models import Work
from src.backend.library.reviews.dependencies import is_review_owner
from src.backend.library.reviews.exceptions import ReviewNotFound, EmptyReviewError
from src.backend.library.reviews.filters import ReviewFilter
from src.backend.library.reviews.models import Review
from src.backend.library.reviews.repositories.review import ReviewRepository
from src.backend.library.reviews.schemas import CreateReview, UpdateReview


class ReviewManager:
    """Handles business logic for reviews: creation, updates, deletion, and retrieval."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.review_repo = ReviewRepository(session)

    async def create_review(
            self,
            user: User,
            work: Work,
            request: CreateReview
    ) -> Review:
        """Creates a new review for a work.

        Args:
            user: User creating the review.
            work: Work being reviewed.
            request: CreateReview payload with rating, text, and spoiler flag.

        Returns:
            Newly created Review instance.

        Raises:
            EmptyReviewError: When the review has neither a rating nor text.
        """
        if not request.rating and not request.text:
            raise EmptyReviewError("Review should contain either rating or text")

        result = await self.review_repo.create_review(
            work_id=work.id,
            user_id=user.id,
            rating=request.rating,
            text=request.text,
            contains_spoiler=request.contains_spoiler
        )
        await self.session.commit()
        return await self.review_repo.get_review_by_id(result.id)

    async def update_review(
            self,
            user: User,
            review: Review,
            request: UpdateReview
    ) -> None:
        """Updates a review's rating, text, and/or spoiler flag.

        Args:
            user: User requesting the update; must own the review.
            review: Review instance to update.
            request: UpdateReview payload with the fields to change.

        Raises:
            IsNotReviewOwnerError: When the user did not create the review.
        """
        await is_review_owner(user, review)
        await self.review_repo.update_review(review, request.rating, request.text, request.contains_spoiler)
        await self.review_repo.update_is_edited(review, True)
        await self.session.commit()

    async def delete_review(
            self,
            user: User,
            review: Review,
    ) -> None:
        """Deletes a review owned by the given user.

        Args:
            user: User requesting the deletion; must own the review.
            review: Review instance to delete.

        Raises:
            IsNotReviewOwnerError: When the user did not create the review.
        """
        await is_review_owner(user, review)
        await self.review_repo.delete_review(review)
        await self.session.commit()

    async def admin_delete_review(
            self,
            user: User,
            review: Review,
    ) -> None:
        """Deletes a review on behalf of an admin, regardless of ownership.

        Args:
            user: User requesting the deletion; must be an admin.
            review: Review instance to delete.

        Raises:
            PermissionDeniedError: When the user is not an admin.
        """
        await is_admin(user)
        await self.review_repo.delete_review(review)
        await self.session.commit()


    async def get_work_reviews(
            self,
            filters: ReviewFilter,
            work: Work,
    ) -> list[Review]:
        """Lists reviews for a work matching the given filters.

        Args:
            filters: ReviewFilter with search, rating, and ordering criteria.
            work: Work to list reviews for.

        Returns:
            List of matching Review instances.
        """
        result = await self.review_repo.get_work_reviews(work.id, filters)
        return result

    async def get_review_by_id(
            self,
            review_id: int,
    ) -> Review:
        """Fetches a single review by ID.

        Args:
            review_id: ID of the review to fetch.

        Returns:
            Matching Review instance.

        Raises:
            ReviewNotFound: When no review matches the ID.
        """
        result = await self.review_repo.get_review_by_id(review_id)
        if not result:
            raise ReviewNotFound("Review not found")
        return result

    async def get_average_rating(
            self,
            work: Work,
    ) -> float:
        """Computes the average rating across a work's reviews.

        Args:
            work: Work to compute the average rating for.

        Returns:
            Average rating across the work's reviews, or 0 if none have a rating.
        """
        result = await self.review_repo.get_work_reviews(work.id)
        ratings = [r.rating for r in result]
        return sum(ratings)/ len(ratings) if ratings else 0

