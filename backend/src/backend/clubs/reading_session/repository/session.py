from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.models import ReadingSession
from src.backend.clubs.reading_session.schemas import ReadingSessionStatus


@dataclass
class ReadingSessionRepository:
    """Data access layer for ReadingSession model operations."""

    session: AsyncSession

    async def create_session(
            self,
            club_id: int,
            work_id: int,
            deadline: datetime,
            created_by_id: int,
    ) -> ReadingSession:
        """Creates and persists a new reading session record.

        Args:
            club_id: ID of the club.
            work_id: ID of the work.
            deadline: Session deadline datetime.
            created_by_id: ID of the user creating the session.

        Returns:
            Newly created ReadingSession instance.
        """
        result = ReadingSession(
            club_id=club_id,
            work_id=work_id,
            deadline=deadline,
            created_by_id=created_by_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_session_status(
            self,
            reading_session: ReadingSession,
            status: str
    ) -> None:
        """Updates the status of a reading session.

        Args:
            reading_session: ReadingSession instance to update.
            status: New status string.
        """
        reading_session.status = status
        self.session.add(reading_session)
        await self.session.flush()

    async def update_session_completed(
            self,
            reading_session: ReadingSession,
            completed_at: datetime
    ) -> None:
        """Sets the completed_at timestamp on a reading session.

        Args:
            reading_session: ReadingSession instance to update.
            completed_at: Datetime when the session was completed.
        """
        reading_session.completed_at = completed_at
        self.session.add(reading_session)
        await self.session.flush()

    async def delete_session(
            self,
            reading_session: ReadingSession
    ) -> None:
        """Deletes a reading session record and flushes the session.

        Args:
            reading_session: ReadingSession instance to delete.
        """
        await self.session.delete(reading_session)
        await self.session.flush()

    async def get_club_active_sessions(
            self,
            club_id: int
    ) -> list[ReadingSession]:
        """Returns the currently active sessions for a club

        Args:
            club_id: ID of the club.

        Returns:
            Active ReadingSession instances
        """
        stmt = select(ReadingSession).where(
            and_(
                ReadingSession.club_id == club_id,
                ReadingSession.status == ReadingSessionStatus.active
            ))
        result = await self.session.execute(stmt)
        sessions = result.scalars().all()
        return sessions

    async def get_club_sessions(
            self,
            club_id: int
    ) -> list[ReadingSession]:
        """Returns all reading sessions for a club.

        Args:
            club_id: ID of the club.

        Returns:
            List of ReadingSession instances.
        """
        stmt = select(ReadingSession).where(ReadingSession.club_id == club_id)
        result = await self.session.execute(stmt)
        sessions = result.scalars().all()
        return sessions

    async def get_session_by_id(
            self,
            session_id: int
    ) -> ReadingSession | None:
        """Fetches a reading session by its ID.

        Args:
            session_id: ID of the reading session.

        Returns:
            ReadingSession instance if found, None otherwise.
        """
        stmt = select(ReadingSession).where(ReadingSession.id == session_id)
        result = await self.session.execute(stmt)
        sessions = result.scalar_one_or_none()
        return sessions

    async def exists_active_work_session(
            self,
            work_id: int
    ) -> ReadingSession | None:
        stmt = select(ReadingSession).where(
            and_(
                ReadingSession.work_id == work_id,
                ReadingSession.completed_at == None
            )
        )
        result = await self.session.execute(stmt)
        sessions = result.scalar_one_or_none()
        return sessions
