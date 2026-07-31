from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.dependencies import get_milestone_or_404
from src.backend.clubs.reading_session.models import Milestone
from src.backend.clubs.thread.exceptions import ThreadNotInMilestoneError
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.thread.exceptions import PostNotInThreadError, ReactionNotInPostError, ThreadNotInClubError
from src.backend.clubs.thread.models import PostReaction
from src.backend.clubs.thread.exceptions import IsNotPostOwnerError, IsNotPostReactionOwnerError
from src.backend.identity.auth.models import User
from src.backend.clubs.thread.managers.thread import ThreadManager
from src.backend.clubs.thread.models import Thread, Post
from src.backend.core.dependencies import get_db


async def get_thread_manager(
        session: AsyncSession = Depends(get_db)
) -> ThreadManager:
    return ThreadManager(session)

async def get_thread_general_or_404(
        thread_id: int,
        club: Club = Depends(get_club_or_404),
        manager: ThreadManager = Depends(get_thread_manager)
) -> Thread:
    thread = await manager.get_thread_by_id(thread_id)
    if thread.club_id != club.id:
        raise ThreadNotInClubError("Thread not found in this club")
    return thread

async def get_thread_session_or_404(
        thread_id: int,
        milestone: Milestone = Depends(get_milestone_or_404),
        manager: ThreadManager = Depends(get_thread_manager)
) -> Thread:
    thread = await manager.get_thread_by_id(thread_id)
    if thread.club_id != milestone.id:
        raise ThreadNotInMilestoneError("Thread not found in this club")
    return thread


async def is_post_owner(
        post: Post,
        user: User,
):
    if post.author_id != user.id:
        raise IsNotPostOwnerError("Is not post owner")
    return True

from src.backend.clubs.thread.managers.posts import PostManager

async def get_post_manager(
        session: AsyncSession = Depends(get_db)
) -> PostManager:
    return PostManager(session)

async def get_post_general_or_404(
        post_id: int,
        thread: Thread = Depends(get_thread_general_or_404),
        manager: PostManager = Depends(get_post_manager)
) -> Post:
    post = await manager.get_post_by_id(post_id)
    if post.thread_id != thread.id:
        raise PostNotInThreadError("Post not found in this thread")
    return post

async def get_post_session_or_404(
        post_id: int,
        thread: Thread = Depends(get_thread_general_or_404),
        manager: PostManager = Depends(get_post_manager)
) -> Post:
    post = await manager.get_post_by_id(post_id)
    if post.thread_id != thread.id:
        raise PostNotInThreadError("Post not found in this thread")
    return post


async def is_reaction_owner(
        reaction: PostReaction,
        user: User,
):
    if reaction.user_id != user.id:
        raise IsNotPostReactionOwnerError("Is not reaction owner")
    return True

from src.backend.clubs.thread.managers.reaction import PostReactionManager

async def get_post_reaction_manager(
        session: AsyncSession = Depends(get_db)
) -> PostReactionManager:
    return PostReactionManager(session)

async def get_post_reaction_general_or_404(
        reaction_id: int,
        post: Post = Depends(get_post_general_or_404),
        manager: PostReactionManager = Depends(get_post_reaction_manager)
) -> PostReaction:
    reaction = await manager.get_reaction_by_id(reaction_id)
    if reaction.post_id != post.id:
        raise ReactionNotInPostError("Reaction not found in this post")
    return reaction

async def get_post_reaction_session_or_404(
        reaction_id: int,
        post: Post = Depends(get_post_session_or_404),
        manager: PostReactionManager = Depends(get_post_reaction_manager)
) -> PostReaction:
    reaction = await manager.get_reaction_by_id(reaction_id)
    if reaction.post_id != post.id:
        raise ReactionNotInPostError("Reaction not found in this post")
    return reaction