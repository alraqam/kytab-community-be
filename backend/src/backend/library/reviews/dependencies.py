from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.auth.models import User
from src.backend.library.reviews.exceptions import IsNotReviewOwnerError, IsNotReviewCommentOwnerError, \
    IsNotReviewLikeOwnerError
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
        manager: ReviewManager = Depends(get_review_manager)
) -> Review:
    return await manager.get_review_by_id(review_id)


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
        manager: ReviewCommentManager = Depends(get_review_comment_manager)
) -> ReviewComment:
    return await manager.get_comment_by_id(comment_id)


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
        manager: ReviewLikeManager = Depends(get_review_like_manager)
) -> ReviewLike:
    return await manager.get_like_by_id(like_id)