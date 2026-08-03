from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.voting.models import PollCandidate


@dataclass
class PollCandidateRepository:
    """Data access layer for PollCandidate model operations."""

    session: AsyncSession

    async def create_poll_candidate(
            self,
            poll_id: int,
            work_id: int,
    ) -> PollCandidate:
        """Creates and persists a new poll candidate record.

        Args:
            poll_id: ID of the voting poll.
            work_id: ID of the work being nominated.

        Returns:
            Newly created PollCandidate instance.
        """
        result = PollCandidate(
            poll_id=poll_id,
            work_id=work_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_poll_candidates(
            self,
            poll_id: int,
    ) -> list[PollCandidate]:
        """Returns all candidates for a voting poll.

        Args:
            poll_id: ID of the voting poll.

        Returns:
            List of PollCandidate instances.
        """
        stmt = select(PollCandidate).where(
            and_(
                PollCandidate.poll_id == poll_id,
            )
        )
        result = await self.session.execute(stmt)
        poll = result.scalars().all()
        return poll

    async def get_poll_candidate_by_id(
            self,
            candidate_id: int,
    ) -> PollCandidate | None:
        """Fetches a poll candidate by its ID.

        Args:
            candidate_id: ID of the poll candidate.

        Returns:
            PollCandidate instance if found, None otherwise.
        """
        stmt = select(PollCandidate).where(PollCandidate.id == candidate_id)
        result = await self.session.execute(stmt)
        candidate = result.scalar_one_or_none()
        return candidate