from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.voting.dependencies import get_voting_poll_or_404, get_vote_poll_manager
from src.backend.clubs.voting.managers.vote_poll import VotePollManager
from src.backend.clubs.voting.models import VotingPoll
from src.backend.clubs.voting.schemas import GetPollVote, CreatePollVote
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{poll_id}/vote",
    tags=["votes"]
)


@cbv(router)
class PollCandidateRouter:
    """CBV router for poll vote endpoints."""

    manager: VotePollManager = Depends(get_vote_poll_manager)
    club: Club = Depends(get_club_or_404)
    user: User = Depends(get_current_user)
    poll: VotingPoll = Depends(get_voting_poll_or_404)

    @router.post(
        "/",
        summary="voting",
        response_model=GetPollVote,
    )
    async def vote(
            self,
            request: CreatePollVote,
    ):
        """Casts a vote for a candidate in the current poll."""
        result = await self.manager.vote(self.user, self.club, self.poll, request)
        return result

    @router.get(
        "/",
        summary="getting poll votes",
        response_model=list[GetPollVote],
    )
    async def get_poll_votes(self) -> list[GetPollVote]:
        """Returns all votes cast in the current voting poll."""
        result = await self.manager.get_poll_votes(self.club, self.user, self.poll)
        return result



