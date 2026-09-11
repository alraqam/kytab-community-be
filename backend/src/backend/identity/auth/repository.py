from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, insert, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import Session, RecoveryCode


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


@dataclass
class RecoveryCodeRepository:
    """Data-access layer for two-factor recovery code persistence and queries."""

    session: AsyncSession

    async def create_many(
            self,
            user_id: int,
            code_hashes: list[str],
    ) -> list[RecoveryCode]:
        """Inserts a batch of hashed recovery codes for a user.

        Args:
            user_id: ID of the user the recovery codes belong to.
            code_hashes: Hashed recovery code strings to store.

        Returns:
            List of newly created RecoveryCode instances.
        """
        stmt = insert(RecoveryCode).values(
            [{"user_id": user_id, "code_hash": code_hash} for code_hash in code_hashes]
        ).returning(RecoveryCode)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return list(result.scalars().all())

    async def get_unused_by_user(
            self,
            user_id: int,
    ) -> list[RecoveryCode]:
        """Lists a user's unused recovery codes.

        Args:
            user_id: ID of the user whose recovery codes are being listed.

        Returns:
            List of unused RecoveryCode instances belonging to the user.
        """
        stmt = select(RecoveryCode).where(
            and_(
                RecoveryCode.user_id == user_id,
                RecoveryCode.used_at == None,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_used(
            self,
            recovery_code: RecoveryCode,
    ) -> None:
        """Stamps a recovery code as used and flushes the session.

        Args:
            recovery_code: RecoveryCode instance to mark used.
        """
        recovery_code.used_at = datetime.now(timezone.utc)
        self.session.add(recovery_code)
        await self.session.flush()

    async def delete_all_for_user(
            self,
            user_id: int,
    ) -> None:
        """Deletes all recovery codes belonging to a user.

        Args:
            user_id: ID of the user whose recovery codes are being deleted.
        """
        stmt = select(RecoveryCode).where(RecoveryCode.user_id == user_id)
        result = await self.session.execute(stmt)
        for recovery_code in result.scalars().all():
            await self.session.delete(recovery_code)
        await self.session.flush()