from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.voting.dependencies import get_poll_candidate_manager, get_voting_poll_or_404
from src.backend.clubs.voting.managers.poll_candidate import PollCandidateManager
from src.backend.clubs.voting.models import VotingPoll
from src.backend.clubs.voting.schemas import GetPollCandidate, CreatePollCandidate
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{poll_id}/candidate",
    tags=["candidates"]
)

@cbv(router)
class PollCandidateRouter:
    """CBV router for poll candidate endpoints."""

    manager: PollCandidateManager = Depends(get_poll_candidate_manager)
    club: Club = Depends(get_club_or_404)
    user: User = Depends(get_current_user)
    poll: VotingPoll = Depends(get_voting_poll_or_404)

    @router.post(
        "/",
        summary="creating poll candidate",
        response_model=GetPollCandidate,
    )
    async def create_poll_candidate(
            self,
            request: CreatePollCandidate,
    ):
        """Adds a book as a candidate to the current poll."""
        result = await self.manager.create_poll_candidate(self.user, self.club, self.poll, request)
        return result


    @router.get(
        "/",
        summary="getting poll candidates",
        response_model=list[GetPollCandidate],
    )
    async def get_poll_candidates(self) -> list[GetPollCandidate]:
        """Returns all candidates for the current voting poll."""
        result = await self.manager.get_poll_candidates(self.club, self.user, self.poll)
        return result



