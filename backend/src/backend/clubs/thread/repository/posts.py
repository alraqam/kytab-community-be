from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.models import Post


@dataclass
class PostRepository:
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
        await self.session.delete(post)
        await self.session.flush()

    async def get_posts(
            self,
            thread_id: int,
    ) -> list[Post]:
        stmt = select(Post).where(
            and_(
                Post.thread_id == thread_id,
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
        stmt = select(Post).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        post = result.scalar_one_or_none()
        return post

