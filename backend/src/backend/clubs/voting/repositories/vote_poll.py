from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.voting.models import PollVote


@dataclass
class VotePollRepository:
    """Data access layer for PollVote model operations."""

    session: AsyncSession

    async def vote(
            self,
            poll_id: int,
            user_id: int,
            candidate_id: int,
    ) -> PollVote:
        """Creates and persists a new poll vote record.

        Args:
            poll_id: ID of the voting poll.
            user_id: ID of the user casting the vote.
            candidate_id: ID of the candidate being voted for.

        Returns:
            Newly created PollVote instance.
        """
        result = PollVote(
            poll_id=poll_id,
            user_id=user_id,
            candidate_id=candidate_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result


    async def get_poll_votes(
            self,
            poll_id: int,
    ) -> list[PollVote]:
        """Returns all votes cast in a voting poll.

        Args:
            poll_id: ID of the voting poll.

        Returns:
            List of PollVote instances.
        """
        stmt = select(PollVote).where(PollVote.poll_id == poll_id,)
        result = await self.session.execute(stmt)
        votes = result.scalars().all()
        return votes

    async def get_poll_vote_by_id(
            self,
            vote_id: int,
    ) -> PollVote | None:
        """Fetches a poll vote by its ID.

        Args:
            vote_id: ID of the poll vote.

        Returns:
            PollVote instance if found, None otherwise.
        """
        stmt = select(PollVote).where(PollVote.id == vote_id)
        result = await self.session.execute(stmt)
        vote = result.scalar_one_or_none()
        return vote