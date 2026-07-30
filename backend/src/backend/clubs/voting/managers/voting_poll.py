from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.reading_session.exceptions import DateInPastError
from src.backend.clubs.voting.managers.poll_candidate import PollCandidateManager
from src.backend.clubs.voting.managers.vote_poll import VotePollManager
from src.backend.clubs.voting.repositories.voting_poll import VotingPollRepository
from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_member
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.voting.exceptions import VotingClosedError, ActivePollAlreadyExistsError, ActivePollError, \
    ActivePollsNotFoundError, PollNotFoundError
from src.backend.clubs.voting.models import VotingPoll
from src.backend.clubs.voting.schemas import VotingStatus, CreateVotingPoll, UpdateVotingPoll
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager


class VotingPollManager:
    """Handles business logic for voting poll lifecycle and results."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.poll_repo = VotingPollRepository(session)
        self.club_manager = ClubManager(session)
        self.user_manager = UserManager(session)
        self.votes_manager = VotePollManager(session)
        self.candidate_manager = PollCandidateManager(session)
        self.membership_manager = ClubMembershipManager(session)

    async def create_poll(
            self,
            user: User,
            club: Club,
            request: CreateVotingPoll
    ) -> VotingPoll:
        """Creates a new voting poll for the club; requires owner or moderator role.

        Args:
            user: Club owner or moderator creating the poll.
            club: Club for which the poll is created.
            request: CreateVotingPoll payload with closes_at datetime.

        Returns:
            Newly created VotingPoll instance.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            DateInPastError: When the closes_at date is in the past.
            ActivePollAlreadyExistsError: When the club already has an active poll.
        """
        is_owner_or_moderator(club, user.id)

        if request.closes_at <= datetime.now(timezone.utc):
            raise DateInPastError("Chosen date is in past")

        exists = await self.poll_repo.get_active_poll(club.id)
        if exists:
            raise ActivePollAlreadyExistsError("Active poll already exists")

        response = await self.poll_repo.create_voting_poll(
            club_id=club.id,
            created_by_id=user.id,
            closes_at=request.closes_at,
        )

        await self.session.commit()
        return response

    async def update_voting_poll(
            self,
            user: User,
            club: Club,
            poll: VotingPoll,
            request: UpdateVotingPoll,
    ) -> None:
        """Updates the closing datetime of a voting poll.

        Args:
            user: Club owner or moderator updating the poll.
            club: Club owning the poll.
            poll: VotingPoll instance to update.
            request: UpdateVotingPoll payload with new closes_at datetime.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            VotingClosedError: When the poll is already closed.
            DateInPastError: When the new closes_at date is in the past.
        """
        is_owner_or_moderator(club, user.id)

        if poll.status == VotingStatus.closed:
            raise VotingClosedError("Voting is closed")

        if request.closes_at <= datetime.now(timezone.utc):
            raise DateInPastError("Chosen date is in past")

        await self.poll_repo.update_voting_poll(
            poll=poll,
            closes_at=request.closes_at
        )
        await self.session.commit()

    async def close_voting_poll(
            self,
            user: User,
            club: Club,
            poll: VotingPoll,
    ) -> None:
        """Closes an active voting poll.

        Args:
            user: Club owner or moderator closing the poll.
            club: Club owning the poll.
            poll: VotingPoll instance to close.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
        """
        is_owner_or_moderator(club, user.id)

        await self.poll_repo.update_voting_poll_status(
            poll=poll,
            status=VotingStatus.closed
        )
        await self.session.commit()

    async def delete_voting_poll(
            self,
            user: User,
            club: Club,
            poll: VotingPoll,
    ) -> None:
        """Deletes a non-active voting poll.

        Args:
            user: Club owner or moderator deleting the poll.
            club: Club owning the poll.
            poll: VotingPoll instance to delete.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            ActivePollError: When the poll is currently active.
        """
        is_owner_or_moderator(club, user.id)

        if poll.status == VotingStatus.active:
            raise ActivePollError("Active voting polls can not be deleted")

        await self.poll_repo.delete_voting_poll(
            poll=poll,
        )
        await self.session.commit()

    async def get_active_poll(
            self,
            user: User,
            club: Club,
    ) -> VotingPoll:
        """Returns the club's currently active voting poll.

        Args:
            user: Authenticated club member requesting the poll.
            club: Club whose active poll is retrieved.

        Returns:
            Active VotingPoll instance.

        Raises:
            NotClubMemberError: When the user is not a club member.
            ActivePollsNotFoundError: When no active poll exists for the club.
        """
        await is_club_member(club, user, self.session)

        poll = await self.poll_repo.get_active_poll(
            club_id=club.id,
        )
        if not poll:
            raise ActivePollsNotFoundError("Active polls not found in this club")
        return poll

    async def get_club_polls(
            self,
            user: User,
            club: Club,
    ) -> list[VotingPoll]:
        """Returns all voting polls for a club.

        Args:
            user: Authenticated club member requesting the polls.
            club: Club whose polls are listed.

        Returns:
            List of VotingPoll instances.

        Raises:
            NotClubMemberError: When the user is not a club member.
        """
        await is_club_member(club, user, self.session)

        polls = await self.poll_repo.get_club_polls(
            club_id=club.id,
        )
        return polls

    async def get_poll_by_id(
            self,
            poll_id: int,
    ) -> VotingPoll:
        """Fetches a voting poll by ID, raising an error if not found.

        Args:
            poll_id: ID of the voting poll.

        Returns:
            VotingPoll instance.

        Raises:
            PollNotFoundError: When no poll with the given ID exists.
        """
        poll = await self.poll_repo.get_poll_by_id(
            poll_id=poll_id,
        )
        if not poll:
            raise PollNotFoundError("Poll not found")
        return poll

    async def get_poll_results(
            self,
            user: User,
            club: Club,
            poll: VotingPoll,
    ) -> list[dict]:
        """Returns vote counts per candidate with work_id for the given poll.

        Args:
            user: Authenticated club member requesting results.
            club: Club owning the poll.
            poll: VotingPoll instance whose results are computed.

        Returns:
            List of dicts with candidate_id, work_id, and vote_count.
        """
        votes = await self.votes_manager.get_poll_votes(club, user, poll)
        candidates = await self.candidate_manager.get_poll_candidates(club, user, poll)

        vote_counts: dict[int, int] = {}
        for vote in votes:
            vote_counts[vote.candidate_id] = vote_counts.get(vote.candidate_id, 0) + 1

        return [
            {
                "candidate_id": c.id,
                "work_id": c.work_id,
                "vote_count": vote_counts.get(c.id, 0),
            }
            for c in candidates
        ]

    async def confirm_winner(
            self,
            user: User,
            club: Club,
            poll: VotingPoll,
    ) -> list[int]:
        """Returns the candidate ID(s) with the highest vote count.

        Args:
            user: Authenticated club member requesting the winner.
            club: Club owning the poll.
            poll: VotingPoll instance whose winner is determined.

        Returns:
            List of candidate IDs that share the maximum vote count.
        """
        results = await self.get_poll_results(user, club, poll)
        if not results:
            return []
        max_count = max(r["vote_count"] for r in results)
        return [r["candidate_id"] for r in results if r["vote_count"] == max_count]

