from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.progress.models import ProgressLog


@dataclass
class ProgressLogRepository:
    session: AsyncSession

    async def create_progress_log(
            self,
            user_id: int,
            period_id: int,
            pages_read: int,
            note: str | None
    ) -> ProgressLog:
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
        log.pages_read += pages_read
        log.note = note
        self.session.add(log)
        await self.session.flush()

    async def get_progress_log_by_id(
            self,
            log_id: int,
    ) -> ProgressLog | None:
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
        stmt = select(ProgressLog).where(ProgressLog.user_id == user_id)
        result = await self.session.execute(stmt)
        logs = result.scalars().all()
        return logs

    async def get_total_pages_read(
            self,
            user_id: int,
            period_id: int,
    ) -> int:
        stmt = select(func.sum(ProgressLog.pages_read)).where(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.period_id == period_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0