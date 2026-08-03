from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.backend.core.dependencies import get_db
from src.backend.identity.blocked_users.managers import BlockedUserManager
from src.backend.identity.blocked_users.models import BlockedUser


async def get_blocked_user_manager(
        session: AsyncSession = Depends(get_db)
) -> BlockedUserManager:
    """Builds a BlockedUserManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        BlockedUserManager instance.
    """
    return BlockedUserManager(session)

async def get_blocked_user_or_404(
        block_id: int,
        manager: BlockedUserManager = Depends(get_blocked_user_manager)
) -> BlockedUser:
    """Resolves a block by path parameter or raises if it doesn't exist.

    Args:
        block_id: ID of the block from the path.
        manager: BlockedUserManager used to look up the block.

    Returns:
        BlockedUser instance.

    Raises:
        BlockNotFoundError: When no block matches the ID.
    """
    return await manager.get_block_by_id(block_id)