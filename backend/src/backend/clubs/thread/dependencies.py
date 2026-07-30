from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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

async def get_thread_or_404(
        thread_id: int,
        manager: ThreadManager = Depends(get_thread_manager)
) -> Thread:
    result = await manager.get_thread_by_id(thread_id)
    return result

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

async def get_post_or_404(
        post_id: int,
        manager: PostManager = Depends(get_post_manager)
) -> Post:
    result = await manager.get_post_by_id(post_id)
    return result

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

async def get_post_reaction_or_404(
        reaction_id: int,
        manager: PostReactionManager = Depends(get_post_reaction_manager)
) -> PostReaction:
    result = await manager.get_reaction_by_id(reaction_id)
    return result