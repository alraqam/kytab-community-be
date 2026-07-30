from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.thread.schemas import GetPost, GetPostPartial
from src.backend.clubs.reading_session.managers.milestone import MilestoneManager
from src.backend.clubs.reading_session.managers.progress import MilestoneProgressManager
from src.backend.clubs.club_membership.services import is_club_member
from src.backend.clubs.thread.dependencies import is_post_owner
from src.backend.clubs.thread.exceptions import LockedThreadError, PostNotFoundError
from src.backend.clubs.thread.managers.thread import ThreadManager
from src.backend.clubs.thread.models import Post, Thread
from src.backend.clubs.thread.repository.posts import PostRepository
from src.backend.clubs.thread.schemas import CreatePost, UpdatePost
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User

class PostManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.post_repo = PostRepository(session)
        self.club_manager = ClubManager(session)
        self.thread_manager = ThreadManager(session)
        self.milestone_progress_manager = MilestoneProgressManager(session)
        self.milestone_manager = MilestoneManager(session)

    async def create_post(
            self,
            user: User,
            club: Club,
            thread: Thread,
            request: CreatePost
    ) -> Post:
        await is_club_member(club, user, self.session)

        if thread.is_locked:
            raise LockedThreadError("Thread is locked")

        if request.parent_post_id:
            parent = await self.post_repo.get_post_by_id(request.parent_post_id)
            if not parent:
                raise PostNotFoundError("Post not found")

        response = await self.post_repo.create_post(
            thread_id=thread.id,
            author_id=user.id,
            title=request.title,
            body=request.body,
            is_spoiler=request.is_spoiler,
            parent_post_id=request.parent_post_id,
        )
        await self.session.commit()
        return response


    async def update_post(
            self,
            user: User,
            thread: Thread,
            post: Post,
            request: UpdatePost
    ) -> None:
        await is_post_owner(post, user)

        if thread.is_locked:
            raise LockedThreadError("Thread is locked")

        await self.post_repo.update_post(
            post=post,
            title=request.title,
            body=request.body,
            is_spoiler=request.is_spoiler,
        )
        await self.session.commit()

    async def delete_post(
            self,
            user: User,
            thread: Thread,
            post: Post,
    ) -> None:
        await is_post_owner(post, user)

        if thread.is_locked:
            raise LockedThreadError("Thread is locked")

        await self.post_repo.delete_post(
            post=post,
        )
        await self.session.commit()

    async def get_all_posts(
            self,
            thread: Thread,
    ) -> list[Post]:
        posts = await self.post_repo.get_posts(
            thread_id=thread.id,
        )
        return posts

    async def get_posts(
            self,
            thread: Thread,
            reading_session: ReadingSession,
            milestone: Milestone,
            user: User,
    ) -> list:
        posts = await self.post_repo.get_posts(
            thread_id=thread.id,
        )

        progress = await self.milestone_progress_manager.get_user_milestone_progress(reading_session, user)

        if not progress:
            spoiler_safe = True

        elif progress.is_finished:
            spoiler_safe = False

        else:
            reached_milestone = await self.milestone_manager.get_milestone_by_id(milestone_id=progress.milestone_id)
            spoiler_safe = milestone.order_index > reached_milestone.order_index

        if spoiler_safe:
            return [
                GetPostPartial(
                    id=post.id,
                    thread_id=post.thread_id,
                    parent_post_id=post.parent_post_id,
                    author_id=post.author_id,
                    title=post.title,
                    is_spoiler=post.is_spoiler,
                    edited_at=post.edited_at,
                    deleted_at=post.deleted_at,
                    created_at=post.created_at,
                )
                for post in posts
            ]

        return [
            GetPost(
                id=post.id,
                thread_id=post.thread_id,
                parent_post_id=post.parent_post_id,
                author_id=post.author_id,
                title=post.title,
                body=post.body,
                is_spoiler=post.is_spoiler,
                edited_at=post.edited_at,
                deleted_at=post.deleted_at,
                created_at=post.created_at,
            )
            for post in posts
        ]


    async def get_post_by_id(
            self,
            post_id: int,
    ) -> Post:
        post = await self.post_repo.get_post_by_id(
            post_id=post_id,
        )
        if not post:
            raise PostNotFoundError("Post not found")
        return post