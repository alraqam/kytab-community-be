from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.exceptions import SessionNotFoundError, NotSessionOwnerError
from src.backend.identity.auth.models import User, Session
from src.backend.identity.auth.repository import SessionRepository
from src.backend.identity.users.repository import UserRepository


class SessionManager:
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
        session = await self.session_repo.get_session_by_id(session_id)
        if session is None:
            raise SessionNotFoundError("Session not found")
        return session

    async def get_user_sessions(
            self,
            user: User
    ) -> list[Session]:
        sessions = await self.session_repo.get_user_active_sessions(user.id)
        return sessions

    async def revoke(
            self,
            user: User,
            session: Session
    ):
        if user.id != session.user_id:
            raise NotSessionOwnerError("Only session owner's can revoke it")
        await self.session_repo.delete(session)
        await self.session.commit()
