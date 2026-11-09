from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.thread.dependencies.thread import get_post_reaction_manager, get_post_general_or_404, get_thread_general_or_404, \
    get_post_reaction_general_or_404
from src.backend.clubs.thread.managers.reaction import PostReactionManager
from src.backend.clubs.thread.models.thread import Thread, Post, PostReaction
from src.backend.clubs.thread.schemas.thread import GetPostReaction, CreatePostReaction
from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{post_id}/reaction",
    tags=["reactions"]
)

@cbv(router)
class PostReactionGeneralRouter:
    """CBV router for reactions on posts within a club-general thread: create, delete, and list."""

    manager: PostReactionManager = Depends(get_post_reaction_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    thread: Thread = Depends(get_thread_general_or_404)
    post: Post = Depends(get_post_general_or_404)

    @router.post(
        "/",
        summary="creating general thread reaction",
        response_model=GetPostReaction,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404, 409),
    )
    async def create_reaction(
            self,
            request: CreatePostReaction
    ):
        """Creates a reaction on a post in the club-general thread."""
        result = await self.manager.create_reaction(self.user, self.club, self.post, request)
        return result

    @router.delete(
        "/{reaction_id}",
        summary="deleting general reaction",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_reaction(
            self,
            reaction: PostReaction = Depends(get_post_reaction_general_or_404)
    ):
        """Deletes a reaction from a post in the club-general thread."""
        await self.manager.delete_reaction(self.user, reaction)

    @router.get(
        "/",
        summary="getting general reactions",
        response_model=list[GetPostReaction],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_post_reactions(
            self,
    ):
        """Lists reactions on a post in the club-general thread."""
        result = await self.manager.get_post_reactions(self.post)
        return result
