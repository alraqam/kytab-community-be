from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.reading_session.dependencies import get_reading_session_or_404, get_milestone_or_404
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.thread.dependencies import get_post_reaction_manager, get_post_session_or_404, get_thread_session_or_404, \
    get_post_reaction_session_or_404
from src.backend.clubs.thread.managers.reaction import PostReactionManager
from src.backend.clubs.thread.models import Thread, Post, PostReaction
from src.backend.clubs.thread.schemas import GetPostReaction, CreatePostReaction
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{post_id}/reaction",
    tags=["reactions"]
)

@cbv(router)
class PostReactionSessionRouter:
    """CBV router for reactions on posts within a reading-session milestone thread: create, delete, and list."""

    manager: PostReactionManager = Depends(get_post_reaction_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    session: ReadingSession = Depends(get_reading_session_or_404)
    milestone: Milestone = Depends(get_milestone_or_404)
    thread: Thread = Depends(get_thread_session_or_404)
    post: Post = Depends(get_post_session_or_404)

    @router.post(
        "/",
        summary="creating session post reaction",
        response_model=GetPostReaction
    )
    async def create_reaction(
            self,
            request: CreatePostReaction
    ):
        """Creates a reaction on a post in the session milestone thread."""
        result = await self.manager.create_reaction(self.user, self.club, self.post, request)
        return result

    @router.delete(
        "/{reaction_id}",
        summary="deleting session post reaction",
    )
    async def delete_reaction(
            self,
            reaction: PostReaction = Depends(get_post_reaction_session_or_404)
    ):
        """Deletes a reaction from a post in the session milestone thread."""
        await self.manager.delete_reaction(self.user, reaction)

    @router.get(
        "/",
        summary="getting session post reactions",
        response_model=list[GetPostReaction]
    )
    async def get_post_reactions(
            self,
    ):
        """Lists reactions on a post in the session milestone thread."""
        result = await self.manager.get_post_reactions(self.post)
        return result
