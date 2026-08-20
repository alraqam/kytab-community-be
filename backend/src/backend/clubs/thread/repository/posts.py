from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.models import Post


@dataclass
class PostRepository:
    """Data-access layer for post persistence and queries."""

    session: AsyncSession

    async def create_post(
            self,
            thread_id: int,
            author_id: int,
            title: str,
            body: str,
            is_spoiler: bool,
            parent_post_id: int | None = None,
    ) -> Post:
        """Inserts a new post into a thread.

        Args:
            thread_id: ID of the thread the post belongs to.
            author_id: ID of the user authoring the post.
            title: Post title.
            body: Post body text.
            is_spoiler: Whether the post contains spoiler content.
            parent_post_id: ID of the parent post being replied to, or None for a top-level post.

        Returns:
            Newly created Post instance.
        """
        result = Post(
            thread_id=thread_id,
            parent_post_id=parent_post_id,
            author_id=author_id,
            title=title,
            body=body,
            is_spoiler=is_spoiler,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_post(
            self,
            post: Post,
            title: str | None = None,
            body: str | None = None,
            is_spoiler: bool | None = None,
    ) -> None:
        """Updates the given fields of a post, skipping unset ones, and stamps the update time.

        Args:
            post: Post instance to update.
            title: New title, or None to leave unchanged.
            body: New body, or None to leave unchanged.
            is_spoiler: New spoiler flag, or None to leave unchanged.
        """
        updates = {
            "title": title,
            "body": body,
            "is_spoiler": is_spoiler,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(post, field, value)
        post.updated_at = datetime.now()
        await self.session.flush()

    async def delete_post(
            self,
            post: Post
    ) -> None:
        """Deletes a post.

        Args:
            post: Post instance to delete.
        """
        await self.session.delete(post)
        await self.session.flush()

    async def get_posts(
            self,
            thread_id: int,
    ) -> list[Post]:
        """Lists non-deleted posts in a thread.

        Args:
            thread_id: ID of the thread to list posts from.

        Returns:
            List of matching Post instances.
        """
        stmt = select(Post).where(
            and_(
                Post.thread_id == thread_id,
                Post.deleted_at == None
            )
        )
        result = await self.session.execute(stmt)
        posts = result.scalars().all()
        return posts

    async def get_user_posts(
            self,
            user_id: int,
    ) -> list[Post]:
        """Lists all non-deleted posts authored by a user, across all threads.

        Args:
            user_id: ID of the user whose posts are being listed.

        Returns:
            List of matching Post instances.
        """
        stmt = select(Post).where(
            and_(
                Post.author_id == user_id,
                Post.deleted_at == None
            )
        )
        result = await self.session.execute(stmt)
        posts = result.scalars().all()
        return posts

    async def get_post_by_id(
            self,
            post_id: int
    ) -> Post | None:
        """Fetches a single post by ID.

        Args:
            post_id: ID of the post to fetch.

        Returns:
            Matching Post instance, or None if not found.
        """
        stmt = select(Post).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        post = result.scalar_one_or_none()
        return post
