from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.catalog.books.models.book import Work
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.library.reviews.dependencies.review import get_review_or_404, get_review_like_manager, get_review_like_or_404
from src.backend.library.reviews.managers.like import ReviewLikeManager
from src.backend.library.reviews.models.review import Review, ReviewLike
from src.backend.library.reviews.schemas.review import GetReviewLike
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{review_id}/likes",
    tags=["review_likes"]
)

@cbv(router)
class ReviewLikeRouter:
    """CBV router for review likes: create, delete, and retrieval."""

    like_manager: ReviewLikeManager = Depends(get_review_like_manager)
    user: User = Depends(get_current_user)
    review: Review = Depends(get_review_or_404)
    work: Work = Depends(get_work_or_404)

    @router.post(
        "/",
        summary="creating like for review",
        response_model=GetReviewLike,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 404, 409),
    )
    async def create_like(
            self,
    ):
        """Creates a like on the review."""
        result = await self.like_manager.create_like(self.user, self.review)
        return result

    @router.delete(
        "/{like_id}",
        summary="deleting review like",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_like(
            self,
            like: ReviewLike = Depends(get_review_like_or_404),
    ):
        """Deletes a review like."""
        await self.like_manager.delete_like(self.user, like)

    @router.get(
        "/count",
        summary="getting review likes count",
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_review_likes_count(self):
        """Returns the number of likes on the review."""
        result = await self.like_manager.get_review_likes_count(self.review)
        return result

    @router.get(
        "/",
        summary="getting review likes",
        response_model=list[GetReviewLike],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_review_likes(self):
        """Lists all likes on the review."""
        result = await self.like_manager.get_review_likes(self.review)
        return result

    @router.get(
        "/{like_id}",
        summary="getting review like by id",
        response_model=GetReviewLike,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_like_by_id(
            self,
            like: ReviewLike = Depends(get_review_like_or_404),
    ):
        """Fetches a single review like by ID."""
        return like