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
    """Verifies that the given user owns the review.

    Args:
        user: User to check ownership for.
        review: Review instance to check.

    Raises:
        IsNotReviewOwnerError: When the user did not create the review.
    """
    if review.user_id != user.id:
        raise IsNotReviewOwnerError("Only review owner can access and change their review")
    return

from src.backend.library.reviews.managers.review import ReviewManager

async def get_review_manager(
        session: AsyncSession = Depends(get_db)
) -> ReviewManager:
    """Builds a ReviewManager for the current request.

    Args:
        session: Async SQLAlchemy session.

    Returns:
        A new ReviewManager instance.
    """
    return ReviewManager(session)

async def get_review_or_404(
        review_id: int,
        work: Work = Depends(get_work_or_404),
        manager: ReviewManager = Depends(get_review_manager)
) -> Review:
    """Resolves a review by ID and verifies it belongs to the given work.

    Args:
        review_id: ID of the review to fetch.
        work: Work instance the review must belong to.
        manager: ReviewManager used to fetch the review.

    Returns:
        Matching Review instance.

    Raises:
        ReviewNotFound: When no review with the given ID exists.
        ReviewNotInWorkError: When the review does not belong to the given work.
    """
    review =  await manager.get_review_by_id(review_id)
    if review.work_id != work.id:
        raise ReviewNotInWorkError("Review not found in this work")
    return review


async def is_review_comment_owner(
        user: User,
        comment: ReviewComment,
) -> None:
    """Verifies that the given user owns the review comment.

    Args:
        user: User to check ownership for.
        comment: ReviewComment instance to check.

    Raises:
        IsNotReviewCommentOwnerError: When the user did not create the comment.
    """
    if comment.user_id != user.id:
        raise IsNotReviewCommentOwnerError("Only comment owner can access and change their review")
    return

from src.backend.library.reviews.managers.comments import ReviewCommentManager

async def get_review_comment_manager(
        session: AsyncSession = Depends(get_db)
) -> ReviewCommentManager:
    """Builds a ReviewCommentManager for the current request.

    Args:
        session: Async SQLAlchemy session.

    Returns:
        A new ReviewCommentManager instance.
    """
    return ReviewCommentManager(session)

async def get_review_comment_or_404(
        comment_id: int,
        review: ReviewComment = Depends(get_review_or_404),
        manager: ReviewCommentManager = Depends(get_review_comment_manager)
) -> ReviewComment:
    """Resolves a review comment by ID and verifies it belongs to the given review.

    Args:
        comment_id: ID of the comment to fetch.
        review: Review instance the comment must belong to.
        manager: ReviewCommentManager used to fetch the comment.

    Returns:
        Matching ReviewComment instance.

    Raises:
        ReviewCommentNotFoundError: When no comment with the given ID exists.
        CommentNotInReviewError: When the comment does not belong to the given review.
    """
    comment = await manager.get_comment_by_id(comment_id)
    if comment.review_id != review.id:
        raise CommentNotInReviewError("Comment not found in this review")
    return comment


async def is_review_like_owner(
        user: User,
        like: ReviewLike,
) -> None:
    """Verifies that the given user owns the review like.

    Args:
        user: User to check ownership for.
        like: ReviewLike instance to check.

    Raises:
        IsNotReviewLikeOwnerError: When the user did not create the like.
    """
    if like.user_id != user.id:
        raise IsNotReviewLikeOwnerError("Only like owner can access and change their review")
    return

from src.backend.library.reviews.managers.like import ReviewLikeManager

async def get_review_like_manager(
        session: AsyncSession = Depends(get_db)
) -> ReviewLikeManager:
    """Builds a ReviewLikeManager for the current request.

    Args:
        session: Async SQLAlchemy session.

    Returns:
        A new ReviewLikeManager instance.
    """
    return ReviewLikeManager(session)

async def get_review_like_or_404(
        like_id: int,
        review: ReviewComment = Depends(get_review_or_404),
        manager: ReviewLikeManager = Depends(get_review_like_manager)
) -> ReviewLike:
    """Resolves a review like by ID and verifies it belongs to the given review.

    Args:
        like_id: ID of the like to fetch.
        review: Review instance the like must belong to.
        manager: ReviewLikeManager used to fetch the like.

    Returns:
        Matching ReviewLike instance.

    Raises:
        ReviewLikeNotFoundError: When no like with the given ID exists.
        LikeNotInReviewError: When the like does not belong to the given review.
    """
    like = await manager.get_like_by_id(like_id)
    if like.review_id != review.id:
        raise LikeNotInReviewError("Like not found in this review")
    return like