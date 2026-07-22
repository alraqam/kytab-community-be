from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.blocked_users.models import BlockedUser


@dataclass
class BlockedUsersRepository:
    session: AsyncSession

    async def block_user(
            self,
            blocker_id: int,
            blocked_id: int
    ) -> BlockedUser:
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
        stmt = select(BlockedUser).where(BlockedUser.blocker_id == user_id)
        result = await self.session.execute(stmt)
        blocked = result.scalars().all()
        return blocked

    async def get_block_by_id(
            self,
            block_id: int
    ) -> BlockedUser | None:
        stmt = select(BlockedUser).where(BlockedUser.id == block_id)
        result = await self.session.execute(stmt)
        blocked = result.scalar_one_or_none()
        return blocked

    async def is_blocked_user(
            self,
            blocker_id: int,
            blocked_id: int
    ) -> BlockedUser | None:
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
        await self.session.delete(block)
        await self.session.flush()
