from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reviews.models import ReviewComment


@dataclass
class ReviewCommentRepository:
    """Data-access layer for review comment persistence and queries."""

    session: AsyncSession

    async def create_comment(
            self,
            user_id: int,
            review_id: int,
            text: str,
    ) -> ReviewComment:
        """Inserts a new comment on a review.

        Args:
            user_id: ID of the user creating the comment.
            review_id: ID of the review being commented on.
            text: Comment text.

        Returns:
            Newly created ReviewComment instance.
        """
        result = ReviewComment(
            user_id=user_id,
            review_id=review_id,
            text=text,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_comment(
            self,
            comment: ReviewComment,
            text: str,
    ) -> None:
        """Updates a comment's text and marks it as edited.

        Args:
            comment: ReviewComment instance to update.
            text: New comment text.
        """
        comment.text = text
        comment.is_edited = True
        self.session.add(comment)
        await self.session.flush()

    async def delete_comment(
            self,
            comment: ReviewComment,
    ) -> None:
        """Deletes a review comment.

        Args:
            comment: ReviewComment instance to delete.
        """
        await self.session.delete(comment)
        await self.session.flush()

    async def get_review_comments(
            self,
            review_id: int
    ) -> list[ReviewComment]:
        """Lists all comments on a review.

        Args:
            review_id: ID of the review to list comments for.

        Returns:
            List of matching ReviewComment instances.
        """
        stmt = select(ReviewComment).where(ReviewComment.review_id == review_id)
        result = await self.session.execute(stmt)
        comments = result.scalars().all()
        return comments

    async def get_comment_by_id(
            self,
            comment_id: int
    ) -> ReviewComment | None:
        """Fetches a single comment by ID.

        Args:
            comment_id: ID of the comment to fetch.

        Returns:
            Matching ReviewComment instance, or None if not found.
        """
        stmt = select(ReviewComment).where(ReviewComment.id == comment_id)
        result = await self.session.execute(stmt)
        comments = result.scalar_one_or_none()
        return comments