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
    """Handles business logic for review comments: creation, updates, deletion, and comment notifications."""

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
        """Creates a comment on a review and notifies the review's author.

        Args:
            user: User creating the comment.
            review: Review instance being commented on.
            request: CreateReviewComment payload with the comment text.

        Returns:
            Newly created ReviewComment instance.
        """
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
        return await self.comment_repo.get_comment_by_id(response.id)

    async def update_comment(
            self,
            user: User,
            comment: ReviewComment,
            request: UpdateReviewComment
    ) -> None:
        """Updates a comment's text.

        Args:
            user: User requesting the update; must own the comment.
            comment: ReviewComment instance to update.
            request: UpdateReviewComment payload with the new text.

        Raises:
            IsNotReviewCommentOwnerError: When the user did not create the comment.
        """
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
        """Deletes a comment owned by the given user.

        Args:
            user: User requesting the deletion; must own the comment.
            comment: ReviewComment instance to delete.

        Raises:
            IsNotReviewCommentOwnerError: When the user did not create the comment.
        """
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
        """Deletes a comment on behalf of an admin, regardless of ownership.

        Args:
            user: User requesting the deletion; must be an admin.
            comment: ReviewComment instance to delete.

        Raises:
            PermissionDeniedError: When the user is not an admin.
        """
        await is_admin(user)

        await self.comment_repo.delete_comment(
            comment=comment,
        )
        await self.session.commit()

    async def get_review_comments(
            self,
            review: Review,
    ) -> list[ReviewComment]:
        """Lists all comments on a review.

        Args:
            review: Review instance to list comments for.

        Returns:
            List of matching ReviewComment instances.
        """
        comments = await self.comment_repo.get_review_comments(review_id=review.id)
        return comments

    async def get_comment_by_id(
            self,
            comment_id: int,
    ) -> ReviewComment:
        """Fetches a single comment by ID.

        Args:
            comment_id: ID of the comment to fetch.

        Returns:
            Matching ReviewComment instance.

        Raises:
            ReviewCommentNotFoundError: When no comment matches the ID.
        """
        result = await self.comment_repo.get_comment_by_id(comment_id=comment_id)
        if not result:
            raise ReviewCommentNotFoundError("Comment not found")
        return result
