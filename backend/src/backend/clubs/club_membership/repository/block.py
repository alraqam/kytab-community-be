from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.models import ClubBlocked


@dataclass
class ClubBlockedRepository:
    """Data-access layer for ClubBlocked model operations."""

    session: AsyncSession

    async def block_user(
            self,
            club_id: int,
            user_id: int
    ) -> ClubBlocked:
        """Inserts a new club block record.

        Args:
            club_id: ID of the club the user is blocked from.
            user_id: ID of the blocked user.

        Returns:
            Newly created ClubBlocked instance.
        """
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
        """Lists all users blocked from a club.

        Args:
            club_id: ID of the club.

        Returns:
            List of ClubBlocked instances.
        """
        stmt = select(ClubBlocked).where(ClubBlocked.club_id == club_id)
        result = await self.session.execute(stmt)
        blocked = result.scalars().all()
        return blocked

    async def get_block_by_id(
            self,
            block_id: int
    ) -> ClubBlocked | None:
        """Fetches a club block record by its ID.

        Args:
            block_id: ID of the block record.

        Returns:
            ClubBlocked instance if found, None otherwise.
        """
        stmt = select(ClubBlocked).where(ClubBlocked.id == block_id)
        result = await self.session.execute(stmt)
        blocked = result.scalar_one_or_none()
        return blocked

    async def is_blocked_member(
            self,
            club_id: int,
            user_id: int
    ) -> ClubBlocked | None:
        """Fetches the block record for a specific user in a specific club, if any.

        Args:
            club_id: ID of the club to check.
            user_id: ID of the user to check.

        Returns:
            ClubBlocked instance if the user is blocked, None otherwise.
        """
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
        """Deletes a club block record and flushes the session.

        Args:
            block: ClubBlocked instance to delete.
        """
        await self.session.delete(block)
        await self.session.flush()
