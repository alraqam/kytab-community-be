from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.managers.work import WorkManager
from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_member
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.core.storage import StorageService
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.voting.exceptions import VotingClosedError, CandidateInPollError, PollCandidateNotFound
from src.backend.clubs.voting.models import VotingPoll, PollCandidate
from src.backend.clubs.voting.repositories.poll_candidate import PollCandidateRepository
from src.backend.clubs.voting.schemas import CreatePollCandidate, VotingStatus
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager


class PollCandidateManager:
    """Handles business logic for poll candidate operations."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.candidate_repo = PollCandidateRepository(session)
        self.club_manager = ClubManager(session, StorageService())
        self.user_manager = UserManager(session)
        self.work_manager = WorkManager(session)

    async def create_poll_candidate(
            self,
            user: User,
            club: Club,
            poll: VotingPoll,
            request: CreatePollCandidate
    ) -> PollCandidate:
        """Adds a work as a candidate to a voting poll; requires owner or moderator role.

        Args:
            user: Club owner or moderator adding the candidate.
            club: Club owning the poll.
            poll: VotingPoll instance to add the candidate to.
            request: CreatePollCandidate payload with work_id.

        Returns:
            Newly created PollCandidate instance.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            VotingClosedError: When the poll is already closed.
            CandidateInPollError: When the work is already a candidate in the poll.
        """
        is_owner_or_moderator(club, user.id)

        if poll.status == VotingStatus.closed:
            raise VotingClosedError("Voting is closed")

        work = await self.work_manager.get_work_by_id(request.work_id)

        try:
            response = await self.candidate_repo.create_poll_candidate(
                poll_id=poll.id,
                work_id=work.id,
            )
            await self.session.commit()
            return response
        except IntegrityError:
            raise CandidateInPollError("Candidate is already in poll")

    async def get_poll_candidates(
            self,
            club: Club,
            user: User,
            poll: VotingPoll,
    ) -> list[PollCandidate]:
        """Returns all candidates for a voting poll.

        Args:
            club: Club owning the poll.
            user: Authenticated club member requesting the candidates.
            poll: VotingPoll instance whose candidates are listed.

        Returns:
            List of PollCandidate instances.

        Raises:
            NotClubMemberError: When the user is not a member of a public club.
            ClubAccessDeniedError: When the user is not a member of a private or
                secret club (indistinguishable from the club not existing).
        """
        await is_club_member(club, user, self.session)

        candidates = await self.candidate_repo.get_poll_candidates(
            poll_id=poll.id,
        )
        return candidates

    async def get_poll_candidate_by_id(
            self,
            candidate_id: int,
    ) -> PollCandidate:
        """Fetches a poll candidate by ID, raising an error if not found.

        Args:
            candidate_id: ID of the poll candidate.

        Returns:
            PollCandidate instance.

        Raises:
            PollCandidateNotFound: When no candidate with the given ID exists.
        """
        candidate = await self.candidate_repo.get_poll_candidate_by_id(
            candidate_id=candidate_id,
        )
        if not candidate:
            raise PollCandidateNotFound("Poll candidate not found")
        return candidate

