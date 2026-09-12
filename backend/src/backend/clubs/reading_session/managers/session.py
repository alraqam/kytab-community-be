from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_club_member
from src.backend.catalog.books.managers.work import WorkManager
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.exceptions import DateInPastError, MaxActiveSessionsError, ActiveSessionError, \
    ReadingSessionNotFound
from src.backend.clubs.reading_session.models import ReadingSession
from src.backend.clubs.reading_session.repository.session import ReadingSessionRepository
from src.backend.clubs.reading_session.schemas import CreateReadingSession, ReadingSessionStatus
from src.backend.identity.auth.models import User


class ReadingSessionManager:
    """Handles business logic for club reading sessions: creation, completion, deletion, and retrieval."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.session_repo = ReadingSessionRepository(session)
        self.work_manager = WorkManager(session)

    async def create_session(
            self,
            user: User,
            club: Club,
            request: CreateReadingSession
    ) -> ReadingSession:
        """Creates a new reading session for a club and work, enforcing session limits and uniqueness.

        Args:
            user: Owner or moderator creating the session.
            club: Club the session belongs to.
            request: CreateReadingSession payload with work_id and deadline.

        Returns:
            Newly created ReadingSession instance.

        Raises:
            IsNotClubOwnerError: When the user is not the club owner or a moderator.
            WorkNotFoundError: When no work with the given ID exists.
            DateInPastError: When the deadline is not in the future.
            MaxActiveSessionsError: When the club already has 3 active sessions.
            ActiveSessionError: When an active session for the same work already exists.
        """
        is_owner_or_moderator(club, user.id)

        work = await self.work_manager.get_work_by_id(request.work_id)
        if request.deadline <= datetime.now(timezone.utc):
            raise DateInPastError("Chosen date is in past")

        exists = await self.session_repo.get_club_active_sessions(club.id)
        if len(exists) >= 3:
            raise MaxActiveSessionsError("Club already has maximum of 3 active sessions")

        exists_active_work = await self.session_repo.exists_active_work_session(work_id=work.id)
        if exists_active_work:
            raise ActiveSessionError("Active session with this work already exists")

        response = await self.session_repo.create_session(
            club_id=club.id,
            work_id=work.id,
            deadline=request.deadline.replace(tzinfo=None),
            created_by_id=user.id,
        )

        await self.session.commit()
        return await self.session_repo.get_session_by_id(response.id)

    async def complete_session(
            self,
            user: User,
            club: Club,
            reading_session: ReadingSession,
    ) -> None:
        """Marks a reading session as completed and stamps the completion time.

        Args:
            user: Owner or moderator completing the session.
            club: Club the session belongs to.
            reading_session: ReadingSession instance to complete.

        Raises:
            IsNotClubOwnerError: When the user is not the club owner or a moderator.
        """
        is_owner_or_moderator(club, user.id)

        await self.session_repo.update_session_completed(
            reading_session=reading_session,
            completed_at=datetime.now()
        )
        await self.session_repo.update_session_status(
            reading_session=reading_session,
            status=ReadingSessionStatus.completed
        )
        await self.session.commit()

    async def delete_session(
            self,
            user: User,
            club: Club,
            reading_session: ReadingSession,
    ) -> None:
        """Deletes a non-active reading session.

        Args:
            user: Owner or moderator deleting the session.
            club: Club the session belongs to.
            reading_session: ReadingSession instance to delete.

        Raises:
            IsNotClubOwnerError: When the user is not the club owner or a moderator.
            ActiveSessionError: When the session is still active.
        """
        is_owner_or_moderator(club, user.id)

        if reading_session.status == ReadingSessionStatus.active:
            raise ActiveSessionError("Active session can not be deleted")

        await self.session_repo.delete_session(
            reading_session=reading_session,
        )
        await self.session.commit()

    async def get_club_active_sessions(
            self,
            club: Club,
            user: User,
    ) -> list[ReadingSession]:
        """Lists a club's currently active reading sessions.

        Args:
            club: Club whose active sessions are listed.
            user: User requesting the sessions; must be a club member.

        Returns:
            List of active ReadingSession instances.

        Raises:
            NotClubMemberError: When the user is not a member of a public club.
            ClubAccessDeniedError: When the user is not a member of a private or
                secret club (indistinguishable from the club not existing).
        """
        await is_club_member(club, user, self.session)
        sessions = await self.session_repo.get_club_active_sessions(
            club_id=club.id,
        )
        return sessions

    async def get_club_sessions(
            self,
            club: Club,
            user: User,
    ) -> list[ReadingSession]:
        """Lists all reading sessions for a club.

        Args:
            club: Club whose sessions are listed.
            user: User requesting the sessions; must be a club member.

        Returns:
            List of ReadingSession instances.

        Raises:
            NotClubMemberError: When the user is not a member of a public club.
            ClubAccessDeniedError: When the user is not a member of a private or
                secret club (indistinguishable from the club not existing).
        """
        await is_club_member(club, user, self.session)
        sessions = await self.session_repo.get_club_sessions(
            club_id=club.id,
        )
        return sessions

    async def get_session_by_id(
            self,
            session_id: int,
    ) -> ReadingSession:
        """Fetches a reading session by ID.

        Args:
            session_id: ID of the reading session to fetch.

        Returns:
            Matching ReadingSession instance.

        Raises:
            ReadingSessionNotFound: When no session matches the ID.
        """
        sessions = await self.session_repo.get_session_by_id(
            session_id=session_id,
        )
        if not sessions:
            raise ReadingSessionNotFound("Reading session not found")
        return sessions