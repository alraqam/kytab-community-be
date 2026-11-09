from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.voting.dependencies.voting import get_poll_candidate_manager, get_voting_poll_or_404
from src.backend.clubs.voting.managers.poll_candidate import PollCandidateManager
from src.backend.clubs.voting.models.voting import VotingPoll
from src.backend.clubs.voting.schemas.voting import GetPollCandidate, CreatePollCandidate
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

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
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(400, 401, 403, 404, 409),
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
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_poll_candidates(self) -> list[GetPollCandidate]:
        """Returns all candidates for the current voting poll."""
        result = await self.manager.get_poll_candidates(self.club, self.user, self.poll)
        return result



