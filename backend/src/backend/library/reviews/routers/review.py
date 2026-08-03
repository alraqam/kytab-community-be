from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.catalog.books.models import Work
from src.backend.library.reviews.dependencies import get_review_manager, get_review_or_404
from src.backend.library.reviews.filters import ReviewFilter
from src.backend.library.reviews.managers.review import ReviewManager
from src.backend.library.reviews.models import Review
from src.backend.library.reviews.schemas import GetReview, CreateReview, UpdateReview

router = APIRouter(
    prefix="/{work_id}/reviews",
    tags=["reviews"]
)

@cbv(router)
class ReviewRouter:
    """CBV router for book reviews: create, update, delete, and retrieval."""

    manager: ReviewManager = Depends(get_review_manager)
    user: User = Depends(get_current_user)
    work: Work = Depends(get_work_or_404)

    @router.post(
        "/",
        summary="creating review",
        response_model=GetReview,
    )
    async def create_review(
            self,
            request: CreateReview,
    ):
        """Creates a new review for the book."""
        result = await self.manager.create_review(self.user, self.work, request)
        return result

    @router.put(
        "/{review_id}",
        summary="updating review",
    )
    async def update_review(
            self,
            request: UpdateReview,
            review: Review = Depends(get_review_or_404)
    ):
        """Updates a review's rating, text, and/or spoiler flag."""
        await self.manager.update_review(self.user, review, request)

    @router.delete(
        "/{review_id}",
        summary="deleting review",
    )
    async def delete_review(
            self,
            review: Review = Depends(get_review_or_404)
    ):
        """Deletes a review."""
        await self.manager.delete_review(self.user, review)

    @router.get(
        "/",
        summary="getting book reviews",
        response_model=list[GetReview],
    )
    async def get_work_reviews(
            self,
            filters: ReviewFilter = FilterDepends(ReviewFilter)
    ):
        """Lists reviews for the book, optionally filtered and sorted."""
        result = await self.manager.get_work_reviews(filters, self.work)
        return result

    @router.get(
        "/average",
        summary="getting average book rating",
    )
    async def get_average_rating(self) -> float:
        """Returns the book's average rating across its reviews."""
        result = await self.manager.get_average_rating(self.work)
        return result

    @router.get(
        "/{review_id}",
        summary="getting review by id",
        response_model=GetReview,
    )
    async def get_review_by_id(
            self,
            review_id: int
    ):
        """Fetches a single review by ID."""
        result = await self.manager.get_review_by_id(review_id)
        return result


