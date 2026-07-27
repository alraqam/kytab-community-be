from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.catalog.books.models import Work
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.library.reviews.dependencies import get_review_or_404, get_review_like_manager, get_review_like_or_404
from src.backend.library.reviews.managers.like import ReviewLikeManager
from src.backend.library.reviews.models import Review, ReviewLike
from src.backend.library.reviews.schemas import GetReviewLike

router = APIRouter(
    prefix="/{review_id}/likes",
    tags=["review_likes"]
)

@cbv(router)
class ReviewLikeRouter:
    like_manager: ReviewLikeManager = Depends(get_review_like_manager)
    user: User = Depends(get_current_user)
    review: Review = Depends(get_review_or_404)
    work: Work = Depends(get_work_or_404)

    @router.post(
        "/",
        summary="creating like for review",
        response_model=GetReviewLike
    )
    async def create_like(
            self,
    ):
        result = await self.like_manager.create_like(self.user, self.review)
        return result

    @router.delete(
        "/{like_id}",
        summary="deleting review like",
    )
    async def delete_like(
            self,
            like: ReviewLike = Depends(get_review_like_or_404),
    ):
        await self.like_manager.delete_like(self.user, like)

    @router.get(
        "/count",
        summary="getting review likes count",
    )
    async def get_review_likes_count(self):
        result = await self.like_manager.get_review_likes_count(self.review)
        return result

    @router.get(
        "/",
        summary="getting review likes",
        response_model=list[GetReviewLike]
    )
    async def get_review_likes(self):
        result = await self.like_manager.get_review_likes(self.review)
        return result

    @router.get(
        "/{like_id}",
        summary="getting review like by id",
        response_model=GetReviewLike
    )
    async def get_like_by_id(
            self,
            like: ReviewLike = Depends(get_review_like_or_404),
    ):
        return like