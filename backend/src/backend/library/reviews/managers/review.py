from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.catalog.books.models import Work
from src.backend.library.reviews.dependencies import is_review_owner
from src.backend.library.reviews.exceptions import ReviewNotFound
from src.backend.library.reviews.filters import ReviewFilter
from src.backend.library.reviews.models import Review
from backend.library.reviews.repositories.review import ReviewRepository
from src.backend.library.reviews.schemas import CreateReview, UpdateReview


class ReviewManager:
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
        result = await self.review_repo.create_review(
            work_id=work.id,
            user_id=user.id,
            rating=request.rating,
            text=request.text,
            contains_spoiler=request.contains_spoiler
        )
        await self.session.commit()
        return result

    async def update_review(
            self,
            user: User,
            review: Review,
            request: UpdateReview
    ) -> None:
        await is_review_owner(user, review)
        await self.review_repo.update_review(review, request.rating, request.text, request.contains_spoiler)
        await self.session.commit()

    async def delete_review(
            self,
            user: User,
            review: Review,
    ) -> None:
        await is_review_owner(user, review)
        await self.review_repo.delete_review(review)
        await self.session.commit()


    async def get_work_reviews(
            self,
            filters: ReviewFilter,
            work: Work,
    ) -> list[Review]:
        result = await self.review_repo.get_work_reviews(work.id, filters)
        return result

    async def get_review_by_id(
            self,
            review_id: int,
    ) -> Review | None:
        result = await self.review_repo.get_review_by_id(review_id)
        if not result:
            raise ReviewNotFound("Review not found")
        return result

    async def get_average_rating(
            self,
            work: Work,
    ) -> float:
        result = await self.review_repo.get_work_reviews(work.id)
        ratings = [r.rating for r in result]
        return sum(ratings)/ len(ratings) if ratings else 0

