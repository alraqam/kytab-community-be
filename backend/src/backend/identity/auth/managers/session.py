from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.exceptions import SessionNotFoundError, NotSessionOwnerError
from src.backend.identity.auth.models import User, Session
from src.backend.identity.auth.repository.session import SessionRepository
from src.backend.identity.users.repository import UserRepository


class SessionManager:
    """Handles session business logic: lookup, listing, and revocation."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)

    async def get_session_by_id(
            self,
            session_id: int
    ):
        """Fetches a single session by ID.

        Args:
            session_id: ID of the session to fetch.

        Returns:
            Matching Session instance.

        Raises:
            SessionNotFoundError: When no session matches the ID.
        """
        session = await self.session_repo.get_session_by_id(session_id)
        if session is None:
            raise SessionNotFoundError("Session not found")
        return session

    async def get_user_sessions(
            self,
            user: User
    ) -> list[Session]:
        """Lists a user's active (non-revoked) sessions.

        Args:
            user: User whose sessions are being listed.

        Returns:
            List of active Session instances belonging to the user.
        """
        sessions = await self.session_repo.get_user_active_sessions(user.id)
        return sessions

    async def revoke(
            self,
            user: User,
            session: Session
    ):
        """Revokes a session on behalf of its owner.

        Args:
            user: User requesting the revocation.
            session: Session instance to revoke.

        Raises:
            NotSessionOwnerError: When the session does not belong to the user.
        """
        if user.id != session.user_id:
            raise NotSessionOwnerError("Only session owner's can revoke it")
        await self.session_repo.delete(session)
        await self.session.commit()
