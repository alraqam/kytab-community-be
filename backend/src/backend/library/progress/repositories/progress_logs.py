from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.progress.exceptions import ProgressLogAlreadyExists
from src.backend.library.progress.models import ProgressLog


@dataclass
class ProgressLogRepository:
    """Data access layer for ProgressLog model operations."""

    session: AsyncSession

    async def create_progress_log(
            self,
            user_id: int,
            period_id: int,
            pages_read: int,
            log_date: date
    ) -> ProgressLog:
        """Creates a new progress log entry; raises on duplicate for the same date.

        Args:
            user_id: ID of the user logging progress.
            session_id: ID of the reading session.
            pages_read: Number of pages read.
            log_date: Date of the progress entry.

        Returns:
            Newly created ProgressLog instance.

        Raises:
            ProgressLogAlreadyExists: When a log entry already exists for this user, session, and date.
        """
        try:
            result = ProgressLog(
                user_id=user_id,
                period_id=period_id,
                pages_read=pages_read,
                log_date=log_date,
            )
            self.session.add(result)
            await self.session.flush()
            return result
        except IntegrityError:
            raise ProgressLogAlreadyExists("Progress log already exists")

    async def update_progress_log(
            self,
            log: ProgressLog,
            pages_read: int
    ) -> None:
        """Adds pages_read to the existing log entry and flushes the session.

        Args:
            log: ProgressLog instance to update.
            pages_read: Additional pages to add to the current count.
        """
        log.pages_read += pages_read
        self.session.add(log)
        await self.session.flush()

    async def get_progress_log_by_id(
            self,
            log_id: int,
    ) -> ProgressLog | None:
        """Fetches a progress log by its ID.

        Args:
            log_id: ID of the progress log.

        Returns:
            ProgressLog instance if found, None otherwise.
        """
        stmt = select(ProgressLog).where(ProgressLog.id == log_id)
        result = await self.session.execute(stmt)
        log = result.scalar_one_or_none()
        return log

    async def get_user_today_progress_log(
            self,
            user_id: int,
            period_id: int,
            log_date: date
    ) -> ProgressLog | None:
        """Returns the progress log for a user on a specific date, if it exists.

        Args:
            user_id: ID of the user.
            reading_period: ID of the reading period.
            log_date: The date to look up.

        Returns:
            ProgressLog instance if found, None otherwise.
        """
        stmt = select(ProgressLog).where(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.period_id == period_id,
                ProgressLog.log_date == log_date,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_period_progress_logs(
            self,
            user_id: int,
            period_id: int,
    ) -> list[ProgressLog]:
        """Returns all progress logs for a user in a specific reading session.

        Args:
            user_id: ID of the user.
            period_id: ID of the reading period.

        Returns:
            List of ProgressLog instances.
        """
        stmt = select(ProgressLog).where(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.period_id == period_id
        ))
        result = await self.session.execute(stmt)
        logs = result.scalars().all()
        return logs

    async def get_user_progress_logs(
            self,
            user_id: int,
    ) -> list[ProgressLog]:
        """Returns all progress logs for a user across all sessions.

        Args:
            user_id: ID of the user.

        Returns:
            List of ProgressLog instances.
        """
        stmt = select(ProgressLog).where(ProgressLog.user_id == user_id)
        result = await self.session.execute(stmt)
        logs = result.scalars().all()
        return logs
