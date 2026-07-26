from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.library.reviews.dependencies import get_review_or_404, get_review_comment_manager, \
    get_review_comment_or_404
from src.backend.library.reviews.managers.comments import ReviewCommentManager
from src.backend.library.reviews.models import Review, ReviewComment
from src.backend.library.reviews.schemas import GetReviewComment, CreateReviewComment, UpdateReviewComment

router = APIRouter(
    prefix="/{review_id}/comments",
    tags=["review_comments"]
)

@cbv(router)
class ReviewCommentRouter:
    comment_manager: ReviewCommentManager = Depends(get_review_comment_manager)
    user: User = Depends(get_current_user)
    review: Review = Depends(get_review_or_404)

    @router.post(
        "/",
        summary="creating comment for review",
        response_model=GetReviewComment
    )
    async def create_comment(
            self,
            request: CreateReviewComment
    ):
        result = await self.comment_manager.create_comment(self.user, self.review, request)
        return result

    @router.put(
        "/{comment_id}",
        summary="updating review comment",
    )
    async def update_comment(
            self,
            request: UpdateReviewComment,
            comment: ReviewComment = Depends(get_review_comment_or_404),
    ):
        await self.comment_manager.update_comment(self.user, comment, request)

    @router.delete(
        "/{comment_id}",
        summary="deleting review comment",
    )
    async def delete_comment(
            self,
            comment: ReviewComment = Depends(get_review_comment_or_404),
    ):
        await self.comment_manager.delete_comment(self.user, comment)

    @router.get(
        "/",
        summary="getting review comments",
        response_model=list[GetReviewComment]
    )
    async def get_review_comments(self):
        result = await self.comment_manager.get_review_comments(self.review)
        return result

    @router.get(
        "/{comment_id}",
        summary="getting review comment by id",
        response_model=GetReviewComment
    )
    async def get_comment_by_id(
            self,
            comment: ReviewComment = Depends(get_review_comment_or_404),
    ):
        return comment