from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import Session


@dataclass
class SessionRepository:
    """Data-access layer for session persistence and queries."""

    session: AsyncSession

    async def get_session_by_id(
            self,
            session_id: int
    ) -> Session | None:
        """Fetches a single session by ID.

        Args:
            session_id: ID of the session to fetch.

        Returns:
            Matching Session instance, or None if not found.
        """
        stmt = select(Session).where(Session.id == session_id)
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        return session

    async def get_session_by_hash_token(
            self,
            hash_token: str
    ) -> Session | None:
        """Fetches a session by its hashed refresh token.

        Args:
            hash_token: Hashed refresh token to look up.

        Returns:
            Matching Session instance, or None if not found.
        """
        stmt = select(Session).where(Session.refresh_token_hash == hash_token)
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        return session

    async def get_user_active_sessions(
            self,
            user_id: int
    ) -> list[Session]:
        """Lists a user's active (non-revoked) sessions.

        Args:
            user_id: ID of the user whose sessions are being listed.

        Returns:
            List of active Session instances belonging to the user.
        """
        stmt = select(Session).where(
            and_(
                Session.revoked_at == None,
                Session.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        sessions = result.scalars().all()
        return sessions

    async def create(
            self,
            user_id: int,
            refresh_token_hash: str,
            device_label: str,
            ip_address: str,
    ) -> Session:
        """Inserts a new session that expires 30 days from now.

        Args:
            user_id: ID of the user the session belongs to.
            refresh_token_hash: Hashed refresh token identifying the session.
            device_label: Human-readable label for the originating device.
            ip_address: IP address the session was created from.

        Returns:
            Newly created Session instance.
        """
        stmt = insert(Session).values(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            device_label=device_label,
            ip_address=ip_address,
            last_active_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        ).returning(Session)
        result = await self.session.execute(stmt)
        await self.session.flush()
        sessions = result.scalars().first()
        return sessions


    async def update_activity(
            self,
            session: Session,
    ) -> None:
        """Stamps a session's last-active time as now and persists it.

        Args:
            session: Session instance to update.
        """
        session.last_active_at = datetime.now(timezone.utc)
        self.session.add(session)
        await self.session.flush()

    async def update(
            self,
            session: Session,
    ) -> None:
        """Persists changes made to a session instance.

        Args:
            session: Session instance to save.
        """
        self.session.add(session)
        await self.session.flush()

    async def delete(
            self,
            session: Session,
    ) -> None:
        """Revokes a session by stamping its revoked_at time.

        Args:
            session: Session instance to revoke.
        """
        session.revoked_at = datetime.now(timezone.utc)
        self.session.add(session)
        await self.session.flush()
