from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.reading_session.dependencies import get_reading_session_or_404, get_milestone_or_404
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.thread.dependencies import get_post_manager, get_thread_session_or_404, get_post_session_or_404
from src.backend.clubs.thread.managers.posts import PostManager
from src.backend.clubs.thread.models import Thread, Post
from src.backend.clubs.thread.schemas import GetPost, CreatePost, UpdatePost, GetPostPartial
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{thread_id}/post",
    tags=["posts"]
)

@cbv(router)
class PostSessionRouter:
    manager: PostManager = Depends(get_post_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    reading_session: ReadingSession = Depends(get_reading_session_or_404)
    milestone: Milestone = Depends(get_milestone_or_404)
    thread: Thread = Depends(get_thread_session_or_404)

    @router.post(
        "/",
        summary="creating session thread post",
        response_model=GetPost
    )
    async def create_post(
            self,
            request: CreatePost
    ):
        result = await self.manager.create_post(self.user, self.club, self.thread, request)
        return result

    @router.put(
        "/{post_id}",
        summary="update session post",
    )
    async def update_post(
            self,
            request: UpdatePost,
            post: Post = Depends(get_post_session_or_404),
    ):
        await self.manager.update_post(self.user, self.thread, post, request)

    @router.delete(
        "/{post_id}",
        summary="deleting session post",
    )
    async def delete_post(
            self,
            post: Post = Depends(get_post_session_or_404)
    ):
        await self.manager.delete_post(self.user, self.club, self.thread, post)

    @router.get(
        "/",
        summary="getting session posts by user milestone reached",
        response_model=list[GetPost] | list[GetPostPartial]
    )
    async def get_posts(
            self,
    ):
        result = await self.manager.get_posts(self.club, self.thread, self.reading_session, self.milestone, self.user)
        return result

    @router.get(
        "/{post_id}/reveal",
        summary="getting and revealing post by id",
        response_model=GetPost
    )
    async def get_session_milestone_threads(
            self,
            post: Post = Depends(get_post_session_or_404),
    ):
        return await self.manager.reveal_post(self.club, self.user, post)