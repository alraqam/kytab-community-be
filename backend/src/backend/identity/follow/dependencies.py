from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.backend.core.dependencies import get_db
from src.backend.identity.follow.managers import FollowManager
from src.backend.identity.follow.models import Follow


async def get_follow_manager(
        session: AsyncSession = Depends(get_db)
) -> FollowManager:
    return FollowManager(session)

async def get_follow_or_404(
        follow_id: int,
        manager: FollowManager = Depends(get_follow_manager)
) -> Follow:
    return await manager.get_follow_by_id(follow_id)