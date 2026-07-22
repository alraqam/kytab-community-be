from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.backend.core.dependencies import get_db
from src.backend.identity.blocked_users.managers import BlockedUserManager
from src.backend.identity.blocked_users.models import BlockedUser


async def get_blocked_user_manager(
        session: AsyncSession = Depends(get_db)
) -> BlockedUserManager:
    return BlockedUserManager(session)

async def get_blocked_user_or_404(
        block_id: int,
        manager: BlockedUserManager = Depends(get_blocked_user_manager)
) -> BlockedUser:
    return await manager.get_block_by_id(block_id)