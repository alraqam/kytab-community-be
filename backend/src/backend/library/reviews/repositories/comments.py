from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reviews.models import ReviewComment


@dataclass
class ReviewCommentRepository:
    session: AsyncSession

    async def create_comment(
            self,
            user_id: int,
            review_id: int,
            text: str,
    ) -> ReviewComment:
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
        comment.text = text
        comment.is_edited = True
        self.session.add(comment)
        await self.session.flush()

    async def delete_comment(
            self,
            comment: ReviewComment,
    ) -> None:
        await self.session.delete(comment)
        await self.session.flush()

    async def get_review_comments(
            self,
            review_id: int
    ) -> list[ReviewComment]:
        stmt = select(ReviewComment).where(ReviewComment.review_id == review_id)
        result = await self.session.execute(stmt)
        comments = result.scalars().all()
        return comments

    async def get_comment_by_id(
            self,
            comment_id: int
    ) -> ReviewComment | None:
        stmt = select(ReviewComment).where(ReviewComment.id == comment_id)
        result = await self.session.execute(stmt)
        comments = result.scalar_one_or_none()
        return comments