from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.models import ClubBlocked


@dataclass
class ClubBlockedRepository:
    session: AsyncSession

    async def block_user(
            self,
            club_id: int,
            user_id: int
    ) -> ClubBlocked:
        result = ClubBlocked(
            club_id=club_id,
            user_id=user_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_club_blocked(
            self,
            club_id: int
    ) -> list[ClubBlocked]:
        stmt = select(ClubBlocked).where(ClubBlocked.club_id == club_id)
        result = await self.session.execute(stmt)
        blocked = result.scalars().all()
        return blocked

    async def get_block_by_id(
            self,
            block_id: int
    ) -> ClubBlocked | None:
        stmt = select(ClubBlocked).where(ClubBlocked.id == block_id)
        result = await self.session.execute(stmt)
        blocked = result.scalar_one_or_none()
        return blocked

    async def is_blocked_member(
            self,
            club_id: int,
            user_id: int
    ) -> ClubBlocked | None:
        stmt = select(ClubBlocked).where(
            and_(
                ClubBlocked.club_id == club_id,
                ClubBlocked.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        blocked = result.scalar_one_or_none()
        return blocked

    async def delete_block(
            self,
            block: ClubBlocked
    ) -> None:
        await self.session.delete(block)
        await self.session.flush()
