from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.voting.repositories.vote_poll import VotePollRepository
from src.backend.clubs.club_membership.services import is_club_member
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.voting.exceptions import VotingClosedError, UserVoteExistsError, PollVoteNotFoundError
from src.backend.clubs.voting.models import VotingPoll, PollVote
from src.backend.clubs.voting.schemas import VotingStatus, CreatePollVote
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager



class VotePollManager:
    """Handles business logic for poll voting operations."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.vote_repo = VotePollRepository(session)
        self.club_manager = ClubManager(session)
        self.user_manager = UserManager(session)

    async def vote(
            self,
            user: User,
            club: Club,
            poll: VotingPoll,
            request: CreatePollVote
    ) -> PollVote:
        """Casts a vote for a candidate in a poll.

        Args:
            user: Authenticated club member casting the vote.
            club: Club owning the poll.
            poll: VotingPoll instance to vote in.
            request: CreatePollVote payload with candidate_id.

        Returns:
            Newly created PollVote instance.

        Raises:
            NotClubMemberError: When the user is not a club member.
            VotingClosedError: When the poll is already closed.
            UserVoteExistsError: When the user has already voted in this poll.
        """
        await is_club_member(club, user, self.session)
        if poll.status == VotingStatus.closed:
            raise VotingClosedError("Voting is closed")

        try:
            response = await self.vote_repo.vote(
                poll_id=poll.id,
                user_id=user.id,
                candidate_id=request.candidate_id
            )
            await self.session.commit()
            return response
        except IntegrityError:
            raise UserVoteExistsError("You already voted")

    async def get_poll_votes(
            self,
            club: Club,
            user: User,
            poll: VotingPoll,
    ) -> list[PollVote]:
        """Returns all votes cast in a voting poll.

        Args:
            club: Club owning the poll.
            user: Authenticated club member requesting the votes.
            poll: VotingPoll instance whose votes are listed.

        Returns:
            List of PollVote instances.

        Raises:
            NotClubMemberError: When the user is not a club member.
        """
        await is_club_member(club, user, self.session)

        votes = await self.vote_repo.get_poll_votes(
            poll_id=poll.id,
        )
        return votes

    async def get_poll_vote_by_id(
            self,
            vote_id: int,
    ) -> PollVote:
        """Fetches a poll vote by ID, raising an error if not found.

        Args:
            vote_id: ID of the poll vote.

        Returns:
            PollVote instance.

        Raises:
            PollVoteNotFoundError: When no vote with the given ID exists.
        """
        vote = await self.vote_repo.get_poll_vote_by_id(
            vote_id=vote_id,
        )
        if not vote:
            raise PollVoteNotFoundError("Poll vote not found")
        return vote

