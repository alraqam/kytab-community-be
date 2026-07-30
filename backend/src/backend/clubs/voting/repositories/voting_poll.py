from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.voting.models import VotingPoll
from src.backend.clubs.voting.schemas import VotingStatus


@dataclass
class VotingPollRepository:
    """Data access layer for VotingPoll model operations."""

    session: AsyncSession

    async def create_voting_poll(
            self,
            club_id: int,
            created_by_id: int,
            closes_at: datetime,
    ) -> VotingPoll:
        """Creates and persists a new voting poll with active status.

        Args:
            club_id: ID of the club.
            created_by_id: ID of the user creating the poll.
            closes_at: Datetime when the poll closes.

        Returns:
            Newly created VotingPoll instance.
        """
        result = VotingPoll(
            club_id=club_id,
            created_by_id=created_by_id,
            closes_at=closes_at.replace(tzinfo=None),
            status=VotingStatus.active,
        )
        self.session.add(result)
        await self.session.flush()
        return result


    async def update_voting_poll(
            self,
            poll: VotingPoll,
            closes_at: datetime
    ) -> None:
        """Updates the closing datetime of a voting poll.

        Args:
            poll: VotingPoll instance to update.
            closes_at: New closing datetime (timezone-aware; stored as naive).
        """
        poll.closes_at = closes_at.replace(tzinfo=None)
        self.session.add(poll)
        await self.session.flush()

    async def update_voting_poll_status(
            self,
            poll: VotingPoll,
            status: str
    ) -> None:
        """Updates the status of a voting poll.

        Args:
            poll: VotingPoll instance to update.
            status: New status string.
        """
        poll.status = status
        self.session.add(poll)
        await self.session.flush()

    async def delete_voting_poll(
            self,
            poll: VotingPoll,
    ) -> None:
        """Deletes a voting poll record and flushes the session.

        Args:
            poll: VotingPoll instance to delete.
        """
        await self.session.delete(poll)
        await self.session.flush()

    async def get_active_poll(
            self,
            club_id: int,
    ) -> VotingPoll | None:
        """Returns the currently active poll for a club, or None.

        Args:
            club_id: ID of the club.

        Returns:
            Active VotingPoll instance if found, None otherwise.
        """
        stmt = select(VotingPoll).where(
            and_(
                VotingPoll.club_id == club_id,
                VotingPoll.status == VotingStatus.active
            )
        )
        result = await self.session.execute(stmt)
        poll = result.scalar_one_or_none()
        return poll

    async def get_club_polls(
            self,
            club_id: int,
    ) -> list[VotingPoll]:
        """Returns all voting polls for a club.

        Args:
            club_id: ID of the club.

        Returns:
            List of VotingPoll instances.
        """
        stmt = select(VotingPoll).where(
                VotingPoll.club_id == club_id,
        )
        result = await self.session.execute(stmt)
        polls = result.scalars().all()
        return polls

    async def get_poll_by_id(
            self,
            poll_id: int,
    ) -> VotingPoll | None:
        """Fetches a voting poll by its ID.

        Args:
            poll_id: ID of the voting poll.

        Returns:
            VotingPoll instance if found, None otherwise.
        """
        stmt = select(VotingPoll).where(VotingPoll.id == poll_id)
        result = await self.session.execute(stmt)
        poll = result.scalar_one_or_none()
        return poll