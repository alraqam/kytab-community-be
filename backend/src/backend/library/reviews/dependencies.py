from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.dependencies.work import get_work_or_404
from src.backend.catalog.books.models import Work
from src.backend.core.dependencies import get_db
from src.backend.identity.auth.models import User
from src.backend.library.reviews.exceptions import IsNotReviewOwnerError, IsNotReviewCommentOwnerError, \
    IsNotReviewLikeOwnerError, ReviewNotInWorkError, CommentNotInReviewError, LikeNotInReviewError
from src.backend.library.reviews.models import Review, ReviewComment, ReviewLike


async def is_review_owner(
        user: User,
        review: Review,
) -> None:
    if review.user_id != user.id:
        raise IsNotReviewOwnerError("Only review owner can access and change their review")
    return

from src.backend.library.reviews.managers.review import ReviewManager

async def get_review_manager(
        session: AsyncSession = Depends(get_db)
) -> ReviewManager:
    return ReviewManager(session)

async def get_review_or_404(
        review_id: int,
        work: Work = Depends(get_work_or_404),
        manager: ReviewManager = Depends(get_review_manager)
) -> Review:
    review =  await manager.get_review_by_id(review_id)
    if review.work_id != work.id:
        raise ReviewNotInWorkError("Review not found in this work")
    return review


async def is_review_comment_owner(
        user: User,
        comment: ReviewComment,
) -> None:
    if comment.user_id != user.id:
        raise IsNotReviewCommentOwnerError("Only comment owner can access and change their review")
    return

from src.backend.library.reviews.managers.comments import ReviewCommentManager

async def get_review_comment_manager(
        session: AsyncSession = Depends(get_db)
) -> ReviewCommentManager:
    return ReviewCommentManager(session)

async def get_review_comment_or_404(
        comment_id: int,
        review: ReviewComment = Depends(get_review_or_404),
        manager: ReviewCommentManager = Depends(get_review_comment_manager)
) -> ReviewComment:
    comment = await manager.get_comment_by_id(comment_id)
    if comment.review_id != review.id:
        raise CommentNotInReviewError("Comment not found in this review")
    return comment


async def is_review_like_owner(
        user: User,
        like: ReviewLike,
) -> None:
    if like.user_id != user.id:
        raise IsNotReviewLikeOwnerError("Only like owner can access and change their review")
    return

from src.backend.library.reviews.managers.like import ReviewLikeManager

async def get_review_like_manager(
        session: AsyncSession = Depends(get_db)
) -> ReviewLikeManager:
    return ReviewLikeManager(session)

async def get_review_like_or_404(
        like_id: int,
        review: ReviewComment = Depends(get_review_or_404),
        manager: ReviewLikeManager = Depends(get_review_like_manager)
) -> ReviewLike:
    like = await manager.get_like_by_id(like_id)
    if like.review_id != review.id:
        raise LikeNotInReviewError("Like not found in this review")
    return like