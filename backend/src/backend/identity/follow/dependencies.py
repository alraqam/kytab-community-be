from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.backend.core.dependencies import get_db
from src.backend.identity.follow.managers import FollowManager
from src.backend.identity.follow.models import Follow


async def get_follow_manager(
        session: AsyncSession = Depends(get_db)
) -> FollowManager:
    """Builds a FollowManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        FollowManager instance.
    """
    return FollowManager(session)

async def get_follow_or_404(
        follow_id: int,
        manager: FollowManager = Depends(get_follow_manager)
) -> Follow:
    """Resolves a follow relationship by path parameter or raises if it doesn't exist.

    Args:
        follow_id: ID of the follow relationship from the path.
        manager: FollowManager used to look up the follow relationship.

    Returns:
        Follow instance.

    Raises:
        FollowNotFoundError: When no follow relationship matches the ID.
    """
    return await manager.get_follow_by_id(follow_id)