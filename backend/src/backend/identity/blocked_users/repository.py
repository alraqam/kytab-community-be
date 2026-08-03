from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.blocked_users.models import BlockedUser


@dataclass
class BlockedUsersRepository:
    """Data-access layer for blocked-user persistence and queries."""

    session: AsyncSession

    async def block_user(
            self,
            blocker_id: int,
            blocked_id: int
    ) -> BlockedUser:
        """Inserts a new block row.

        Args:
            blocker_id: ID of the user creating the block.
            blocked_id: ID of the user being blocked.

        Returns:
            Newly created BlockedUser instance.
        """
        result = BlockedUser(
            blocker_id=blocker_id,
            blocked_id=blocked_id
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_user_blocked(
            self,
            user_id: int
    ) -> list[BlockedUser]:
        """Lists all blocks created by a given user.

        Args:
            user_id: ID of the user whose blocks are being fetched.

        Returns:
            List of matching BlockedUser instances.
        """
        stmt = select(BlockedUser).where(BlockedUser.blocker_id == user_id)
        result = await self.session.execute(stmt)
        blocked = result.scalars().all()
        return blocked

    async def get_block_by_id(
            self,
            block_id: int
    ) -> BlockedUser | None:
        """Fetches a single block by ID.

        Args:
            block_id: ID of the block to fetch.

        Returns:
            Matching BlockedUser instance, or None if not found.
        """
        stmt = select(BlockedUser).where(BlockedUser.id == block_id)
        result = await self.session.execute(stmt)
        blocked = result.scalar_one_or_none()
        return blocked

    async def is_blocked_user(
            self,
            blocker_id: int,
            blocked_id: int
    ) -> BlockedUser | None:
        """Looks up a block between two specific users.

        Args:
            blocker_id: ID of the user who may have created the block.
            blocked_id: ID of the potentially blocked user.

        Returns:
            Matching BlockedUser instance, or None if no block exists.
        """
        stmt = select(BlockedUser).where(
            and_(
                BlockedUser.blocker_id == blocker_id,
                 BlockedUser.blocked_id == blocked_id,
            )
        )
        result = await self.session.execute(stmt)
        blocked = result.scalar_one_or_none()
        return blocked

    async def delete_block(
            self,
            block: BlockedUser
    ) -> None:
        """Deletes a block row.

        Args:
            block: BlockedUser instance to delete.
        """
        await self.session.delete(block)
        await self.session.flush()
