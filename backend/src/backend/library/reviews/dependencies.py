from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db
from backend.identity.auth.models import User
from backend.library.reviews.exceptions import IsNotReviewOwnerError
from backend.library.reviews.models import Review

async def is_review_owner(
        user: User,
        review: Review,
) -> None:
    if review.user_id != user.id:
        raise IsNotReviewOwnerError("Only review owner can access and change their review")
    return

from src.backend.library.reviews.managers import ReviewManager

async def get_review_manager(
        session: AsyncSession = Depends(get_db)
) -> ReviewManager:
    return ReviewManager(session)

async def get_review_or_404(
        review_id: int,
        manager: ReviewManager = Depends(get_review_manager)
) -> Review:
    return await manager.get_review_by_id(review_id)