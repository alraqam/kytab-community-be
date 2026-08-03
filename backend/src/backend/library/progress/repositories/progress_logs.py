from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.progress.models import ProgressLog


@dataclass
class ProgressLogRepository:
    """Data-access layer for progress log persistence and queries."""

    session: AsyncSession

    async def create_progress_log(
            self,
            user_id: int,
            period_id: int,
            pages_read: int,
            note: str | None
    ) -> ProgressLog:
        """Inserts a new progress log dated today.

        Args:
            user_id: ID of the user the log belongs to.
            period_id: ID of the reading period the log belongs to.
            pages_read: Number of pages read.
            note: Optional note to attach to the log.

        Returns:
            Newly created ProgressLog instance.
        """
        result = ProgressLog(
            user_id=user_id,
            period_id=period_id,
            pages_read=pages_read,
            log_date=date.today(),
            note=note
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_progress_log(
            self,
            log: ProgressLog,
            pages_read: int,
            note: str | None
    ) -> None:
        """Adds pages read to an existing log and replaces its note.

        Args:
            log: ProgressLog instance to update.
            pages_read: Number of pages to add to the existing total.
            note: New note value, replacing the existing one.
        """
        log.pages_read += pages_read
        log.note = note
        self.session.add(log)
        await self.session.flush()

    async def get_progress_log_by_id(
            self,
            log_id: int,
    ) -> ProgressLog | None:
        """Fetches a single progress log by ID.

        Args:
            log_id: ID of the progress log to fetch.

        Returns:
            Matching ProgressLog instance, or None if not found.
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
        """Fetches a user's progress log for a specific reading period and date.

        Args:
            user_id: ID of the user whose log is fetched.
            period_id: ID of the reading period the log belongs to.
            log_date: Date of the log to fetch.

        Returns:
            Matching ProgressLog instance, or None if not found.
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
        """Lists a user's progress logs within a reading period.

        Args:
            user_id: ID of the user whose logs are listed.
            period_id: ID of the reading period to filter by.

        Returns:
            List of matching ProgressLog instances.
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
        """Lists all progress logs belonging to a user.

        Args:
            user_id: ID of the user whose logs are listed.

        Returns:
            List of matching ProgressLog instances.
        """
        stmt = select(ProgressLog).where(ProgressLog.user_id == user_id)
        result = await self.session.execute(stmt)
        logs = result.scalars().all()
        return logs

    async def get_total_pages_read(
            self,
            user_id: int,
            period_id: int,
    ) -> int:
        """Sums the pages read across a user's logs within a reading period.

        Args:
            user_id: ID of the user whose logs are summed.
            period_id: ID of the reading period to filter by.

        Returns:
            Total pages read, or 0 if no logs exist.
        """
        stmt = select(func.sum(ProgressLog.pages_read)).where(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.period_id == period_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0