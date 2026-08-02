from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.identity.users.managers import UserManager
from src.backend.library.reviews.dependencies import is_review_comment_owner
from src.backend.library.reviews.exceptions import ReviewCommentNotFoundError, ReviewLikeAlreadyExists
from src.backend.library.reviews.models import ReviewComment, Review
from src.backend.library.reviews.repositories.comments import ReviewCommentRepository
from src.backend.library.reviews.schemas import CreateReviewComment, UpdateReviewComment
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType


class ReviewCommentManager:

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.comment_repo = ReviewCommentRepository(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)

    async def create_comment(
            self,
            user: User,
            review: Review,
            request: CreateReviewComment
    ) -> ReviewComment:
        try:
            response = await self.comment_repo.create_comment(
                user_id=user.id,
                review_id=review.id,
                text=request.text,
            )
            await self.session.commit()

            if review.user_id != user.id:
                owner = await self.user_manager.get_user_by_id(review.user_id)
                await self.notification_manager.notify(
                    owner,
                    category=NotificationCategory.general,
                    title=f"{user.username} commented on your review",
                    object_type=NotificationObjectType.comment,
                    object_id=response.id,
                )
            return response
        except IntegrityError:
            raise ReviewLikeAlreadyExists("Like for this review already exists")

    async def update_comment(
            self,
            user: User,
            comment: ReviewComment,
            request: UpdateReviewComment
    ) -> None:
        await is_review_comment_owner(user, comment)

        await self.comment_repo.update_comment(
            comment=comment,
            text=request.text,
        )
        await self.session.commit()

    async def delete_comment(
            self,
            user: User,
            comment: ReviewComment,
    ) -> None:
        await is_review_comment_owner(user, comment)

        await self.comment_repo.delete_comment(
            comment=comment,
        )
        await self.session.commit()

    async def delete_user_comment(
            self,
            user: User,
            comment: ReviewComment,
    ) -> None:
        await is_admin(user)

        await self.comment_repo.delete_comment(
            comment=comment,
        )
        await self.session.commit()

    async def get_review_comments(
            self,
            review: Review,
    ) -> list[ReviewComment]:
        comments = await self.comment_repo.get_review_comments(review_id=review.id)
        return comments

    async def get_comment_by_id(
            self,
            comment_id: int,
    ) -> ReviewComment:
        result = await self.comment_repo.get_comment_by_id(comment_id=comment_id)
        if not result:
            raise ReviewCommentNotFoundError("Comment not found")
        return result
