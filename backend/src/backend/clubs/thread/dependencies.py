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
    """Builds a ThreadManager for the current request.

    Args:
        session: Async SQLAlchemy session, injected via dependency.

    Returns:
        ThreadManager instance bound to the session.
    """
    return ThreadManager(session)

async def get_thread_general_or_404(
        thread_id: int,
        club: Club = Depends(get_club_or_404),
        manager: ThreadManager = Depends(get_thread_manager)
) -> Thread:
    """Resolves a thread by ID and verifies it belongs to the given club.

    Args:
        thread_id: ID of the thread to resolve.
        club: Club instance the thread must belong to.
        manager: ThreadManager used to fetch the thread.

    Returns:
        Thread instance.

    Raises:
        ThreadNotFoundError: When no thread with the given ID exists.
        ThreadNotInClubError: When the thread does not belong to the given club.
    """
    thread = await manager.get_thread_by_id(thread_id)
    if thread.club_id != club.id:
        raise ThreadNotInClubError("Thread not found in this club")
    return thread

async def get_thread_session_or_404(
        thread_id: int,
        milestone: Milestone = Depends(get_milestone_or_404),
        manager: ThreadManager = Depends(get_thread_manager)
) -> Thread:
    """Resolves a thread by ID and verifies it belongs to the given milestone.

    Args:
        thread_id: ID of the thread to resolve.
        milestone: Milestone instance the thread must belong to.
        manager: ThreadManager used to fetch the thread.

    Returns:
        Thread instance.

    Raises:
        ThreadNotFoundError: When no thread with the given ID exists.
        ThreadNotInMilestoneError: When the thread does not belong to the given milestone.
    """
    thread = await manager.get_thread_by_id(thread_id)
    if thread.milestone_id != milestone.id:
        raise ThreadNotInMilestoneError("Thread not found in this club")
    return thread


async def is_post_owner(
        post: Post,
        user: User,
):
    """Checks that the given user authored the given post.

    Args:
        post: Post instance to check ownership of.
        user: User to verify as the author.

    Returns:
        True if the user is the post's author.

    Raises:
        IsNotPostOwnerError: When the user is not the post's author.
    """
    if post.author_id != user.id:
        raise IsNotPostOwnerError("Is not post owner")
    return True

from src.backend.clubs.thread.managers.posts import PostManager

async def get_post_manager(
        session: AsyncSession = Depends(get_db)
) -> PostManager:
    """Builds a PostManager for the current request.

    Args:
        session: Async SQLAlchemy session, injected via dependency.

    Returns:
        PostManager instance bound to the session.
    """
    return PostManager(session)

async def get_post_general_or_404(
        post_id: int,
        thread: Thread = Depends(get_thread_general_or_404),
        manager: PostManager = Depends(get_post_manager)
) -> Post:
    """Resolves a post by ID and verifies it belongs to the given club-general thread.

    Args:
        post_id: ID of the post to resolve.
        thread: Thread instance the post must belong to.
        manager: PostManager used to fetch the post.

    Returns:
        Post instance.

    Raises:
        PostNotFoundError: When no post with the given ID exists.
        PostNotInThreadError: When the post does not belong to the given thread.
    """
    post = await manager.get_post_by_id(post_id)
    if post.thread_id != thread.id:
        raise PostNotInThreadError("Post not found in this thread")
    return post

async def get_post_session_or_404(
        post_id: int,
        thread: Thread = Depends(get_thread_general_or_404),
        manager: PostManager = Depends(get_post_manager)
) -> Post:
    """Resolves a post by ID and verifies it belongs to the given session thread.

    Args:
        post_id: ID of the post to resolve.
        thread: Thread instance the post must belong to.
        manager: PostManager used to fetch the post.

    Returns:
        Post instance.

    Raises:
        PostNotFoundError: When no post with the given ID exists.
        PostNotInThreadError: When the post does not belong to the given thread.
    """
    post = await manager.get_post_by_id(post_id)
    if post.thread_id != thread.id:
        raise PostNotInThreadError("Post not found in this thread")
    return post


async def is_reaction_owner(
        reaction: PostReaction,
        user: User,
):
    """Checks that the given user created the given reaction.

    Args:
        reaction: PostReaction instance to check ownership of.
        user: User to verify as the reaction's creator.

    Returns:
        True if the user created the reaction.

    Raises:
        IsNotPostReactionOwnerError: When the user did not create the reaction.
    """
    if reaction.user_id != user.id:
        raise IsNotPostReactionOwnerError("Is not reaction owner")
    return True

from src.backend.clubs.thread.managers.reaction import PostReactionManager

async def get_post_reaction_manager(
        session: AsyncSession = Depends(get_db)
) -> PostReactionManager:
    """Builds a PostReactionManager for the current request.

    Args:
        session: Async SQLAlchemy session, injected via dependency.

    Returns:
        PostReactionManager instance bound to the session.
    """
    return PostReactionManager(session)

async def get_post_reaction_general_or_404(
        reaction_id: int,
        post: Post = Depends(get_post_general_or_404),
        manager: PostReactionManager = Depends(get_post_reaction_manager)
) -> PostReaction:
    """Resolves a reaction by ID and verifies it belongs to the given post.

    Args:
        reaction_id: ID of the reaction to resolve.
        post: Post instance the reaction must belong to.
        manager: PostReactionManager used to fetch the reaction.

    Returns:
        PostReaction instance.

    Raises:
        ReactionNotFoundError: When no reaction with the given ID exists.
        ReactionNotInPostError: When the reaction does not belong to the given post.
    """
    reaction = await manager.get_reaction_by_id(reaction_id)
    if reaction.post_id != post.id:
        raise ReactionNotInPostError("Reaction not found in this post")
    return reaction

async def get_post_reaction_session_or_404(
        reaction_id: int,
        post: Post = Depends(get_post_session_or_404),
        manager: PostReactionManager = Depends(get_post_reaction_manager)
) -> PostReaction:
    """Resolves a reaction by ID and verifies it belongs to the given post.

    Args:
        reaction_id: ID of the reaction to resolve.
        post: Post instance the reaction must belong to.
        manager: PostReactionManager used to fetch the reaction.

    Returns:
        PostReaction instance.

    Raises:
        ReactionNotFoundError: When no reaction with the given ID exists.
        ReactionNotInPostError: When the reaction does not belong to the given post.
    """
    reaction = await manager.get_reaction_by_id(reaction_id)
    if reaction.post_id != post.id:
        raise ReactionNotInPostError("Reaction not found in this post")
    return reaction
