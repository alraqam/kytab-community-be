from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.voting.exceptions import PollNotInClubError
from src.backend.clubs.voting.managers.poll_candidate import PollCandidateManager
from src.backend.clubs.voting.managers.vote_poll import VotePollManager
from src.backend.clubs.voting.managers.voting_poll import VotingPollManager
from src.backend.clubs.voting.models import VotingPoll, PollCandidate, PollVote
from src.backend.core.dependencies import get_db


async def get_voting_poll_manager(
        session: AsyncSession = Depends(get_db)
) -> VotingPollManager:
    """FastAPI dependency that provides a VotingPollManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        VotingPollManager bound to the current session.
    """
    return VotingPollManager(session)

async def get_voting_poll_or_404(
        poll_id: int,
        club: Club = Depends(get_club_or_404),
        manager: VotingPollManager = Depends(get_voting_poll_manager)
) -> VotingPoll:
    """FastAPI dependency that fetches a voting poll by ID or raises if not found.

    Args:
        poll_id: Voting poll ID from the path parameter.
        manager: VotingPollManager injected by get_voting_poll_manager.

    Returns:
        VotingPoll instance.

    Raises:
        PollNotFoundError: When no poll with the given ID exists.
    """
    poll = await manager.get_poll_by_id(poll_id)
    if poll.club_id == club.id:
        raise PollNotInClubError("Poll not found in club")
    return poll

async def get_poll_candidate_manager(
        session: AsyncSession = Depends(get_db)
) -> PollCandidateManager:
    """FastAPI dependency that provides a PollCandidateManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        PollCandidateManager bound to the current session.
    """
    return PollCandidateManager(session)

async def get_poll_candidate_or_404(
        candidate_id: int,
        manager: PollCandidateManager = Depends(get_poll_candidate_manager)
) -> PollCandidate:
    """FastAPI dependency that fetches a poll candidate by ID or raises if not found.

    Args:
        candidate_id: Candidate ID from the path parameter.
        manager: PollCandidateManager injected by get_poll_candidate_manager.

    Returns:
        PollCandidate instance.

    Raises:
        PollCandidateNotFound: When no candidate with the given ID exists.
    """
    return await manager.get_poll_candidate_by_id(candidate_id)

async def get_vote_poll_manager(
        session: AsyncSession = Depends(get_db)
) -> VotePollManager:
    """FastAPI dependency that provides a VotePollManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        VotePollManager bound to the current session.
    """
    return VotePollManager(session)

async def get_vote_or_404(
        vote_id: int,
        manager: VotePollManager = Depends(get_vote_poll_manager)
) -> PollVote:
    """FastAPI dependency that fetches a poll vote by ID or raises if not found.

    Args:
        vote_id: Vote ID from the path parameter.
        manager: VotePollManager injected by get_vote_poll_manager.

    Returns:
        PollVote instance.

    Raises:
        PollVoteNotFoundError: When no vote with the given ID exists.
    """
    return await manager.get_poll_vote_by_id(vote_id)
