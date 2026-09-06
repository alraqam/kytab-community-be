from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.voting.dependencies import get_voting_poll_or_404, get_voting_poll_manager
from src.backend.clubs.voting.managers.voting_poll import VotingPollManager
from src.backend.clubs.voting.models import VotingPoll
from src.backend.clubs.voting.schemas import GetVotingPoll, CreateVotingPoll, UpdateVotingPoll, GetPollResult
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{club_id}/poll",
)

@cbv(router)
class VotingPollRouter:
    """CBV router for voting poll endpoints."""

    manager: VotingPollManager = Depends(get_voting_poll_manager)
    club: Club = Depends(get_club_or_404)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating poll",
        response_model=GetVotingPoll,
        tags=["polls"],
    )
    async def create_poll(
            self,
            request: CreateVotingPoll,
    ):
        """Creates a new voting poll for the club."""
        result = await self.manager.create_poll(self.user, self.club, request)
        return result

    @router.put(
        "/{poll_id}",
        summary="updating voting poll",
        tags=["polls"],
    )
    async def update_voting_poll(
            self,
            request: UpdateVotingPoll,
            poll: VotingPoll = Depends(get_voting_poll_or_404)
    ):
        """Updates the closing datetime of a voting poll."""
        await self.manager.update_voting_poll(self.user, self.club, poll, request)

    @router.put(
        "/{poll_id}/close",
        summary="closing voting poll",
        tags=["polls"],
    )
    async def close_voting_poll(
            self,
            poll: VotingPoll = Depends(get_voting_poll_or_404)
    ):
        """Closes the specified voting poll."""
        await self.manager.close_voting_poll(self.user, self.club, poll)

    @router.delete(
        "/{poll_id}",
        summary="deleting voting poll",
        tags=["polls"],
    )
    async def delete_voting_poll(
            self,
            poll: VotingPoll = Depends(get_voting_poll_or_404)
    ):
        """Deletes a non-active voting poll."""
        await self.manager.delete_voting_poll(self.user, self.club, poll)

    @router.get(
        "/active",
        summary="getting club's active voting poll",
        response_model=GetVotingPoll,
        tags=["polls"],
    )
    async def get_active_poll(self) -> GetVotingPoll:
        """Returns the club's currently active voting poll."""
        result = await self.manager.get_active_poll(self.user, self.club)
        return result

    @router.get(
        "/",
        summary="getting club's polls",
        tags=["polls"],
    )
    async def get_club_polls(self):
        """Returns all voting polls for the club."""
        result = await self.manager.get_club_polls(self.user, self.club)
        return result

    @router.get(
        "/{poll_id}/results",
        summary="getting poll results",
        response_model=list[GetPollResult],
        tags=["polls"],
    )
    async def get_poll_results(
            self,
            poll: VotingPoll = Depends(get_voting_poll_or_404)
    ):
        """Returns the vote count per candidate for the specified poll."""
        result = await self.manager.get_poll_results(self.user, self.club, poll)
        return result

    @router.get(
        "/{poll_id}/winner",
        summary="getting poll winner/winners",
        tags=["polls"],
    )
    async def confirm_winner(
            self,
            poll: VotingPoll = Depends(get_voting_poll_or_404)
    ):
        """Returns the candidate ID(s) with the most votes."""
        result = await self.manager.confirm_winner(self.user, self.club, poll)
        return result

