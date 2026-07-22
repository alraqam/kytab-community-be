from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, insert, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import Session


@dataclass
class SessionRepository:
    session: AsyncSession

    async def get_session_by_id(
            self,
            session_id: int
    ) -> Session | None:
        stmt = select(Session).where(Session.id == session_id)
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        return session

    async def get_session_by_hash_token(
            self,
            hash_token: str
    ) -> Session | None:
        stmt = select(Session).where(Session.refresh_token_hash == hash_token)
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        return session

    async def get_user_active_sessions(
            self,
            user_id: int
    ) -> list[Session]:
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
        session.last_active_at = datetime.now(timezone.utc)
        self.session.add(session)
        await self.session.flush()

    async def update(
            self,
            session: Session,
    ) -> None:
        self.session.add(session)
        await self.session.flush()

    async def delete(
            self,
            session: Session,
    ) -> None:
        session.revoked_at = datetime.now(timezone.utc)
        self.session.add(session)
        await self.session.flush()