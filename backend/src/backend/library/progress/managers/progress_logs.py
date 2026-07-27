from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.models import Shelf
from src.backend.library.progress.exceptions import ActiveReadingPeriodError
from src.backend.library.progress.managers.reading_period import ReadingPeriodManager
from src.backend.identity.auth.models import User
from src.backend.library.progress.dependencies import is_log_owner
from src.backend.library.progress.exceptions import ProgressLogNotFound, LogDateError
from src.backend.library.progress.models import ReadingPeriod, ProgressLog
from src.backend.library.progress.repositories.progress_logs import ProgressLogRepository
from src.backend.library.progress.schemas import LogProgressSchema


class ProgressLogManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.log_repo = ProgressLogRepository(session)
        self.reading_period_manager = ReadingPeriodManager(session)
        self.shelf_manager = ShelfManager(session)

    async def log_progress(
            self,
            user: User,
            reading_period: ReadingPeriod,
            request: LogProgressSchema
    ) -> ProgressLog:
        if reading_period.finished_at is not None:
            raise ActiveReadingPeriodError("Reading period already finished")

        existing = await self.log_repo.get_user_today_progress_log(
            user_id=user.id,
            period_id=reading_period.id,
            log_date=date.today(),
        )
        if existing:
            await self.log_repo.update_progress_log(existing, request.pages, request.note)
            result = existing
        else:
            result = await self.log_repo.create_progress_log(
                user_id=user.id,
                period_id=reading_period.id,
                pages_read=request.pages,
                note=request.note
            )

        edition = await self.reading_period_manager.get_edition_by_reading_period(reading_period.id)
        total_pages = 0
        if edition:
            total_pages = edition.pages_count

        if result.period_id >=total_pages:
            await self.reading_period_manager.set_finishing_date(user, reading_period)

        await self.session.commit()
        return result

    async def update_today_progress(
            self,
            user: User,
            log: ProgressLog,
            request: LogProgressSchema
    ) -> None:
        await is_log_owner(user, log)
        if log.log_date != date.today():
            raise LogDateError("Can update only today log")
        await self.log_repo.update_progress_log(
            log=log,
            pages_read=request.pages,
            note=request.note
        )
        await self.session.commit()


    async def get_progress_log_by_id(
            self,
            log_id: int,
    ) -> ProgressLog:
        result = await self.log_repo.get_progress_log_by_id(
            log_id=log_id
        )
        if not result:
            raise ProgressLogNotFound("Progress log not found")
        return result

    async def get_user_today_progress_log(
            self,
            user: User,
            reading_period: ReadingPeriod,
    ) -> ProgressLog:
        result = await self.log_repo.get_user_today_progress_log(
            user_id=user.id,
            period_id=reading_period.id,
            log_date=date.today(),
        )
        if not result:
            raise ProgressLogNotFound("Progress log not found")
        return result


    async def get_my_progress_logs(
            self,
            user: User,
    ) -> list[ProgressLog]:
        result = await self.log_repo.get_user_progress_logs(
            user_id=user.id,
        )
        return result

    async def get_users_progress_logs(
            self,
            user: User,
            current_user: User,
            shelf: Shelf
    ) -> list[ProgressLog]:
        await self.shelf_manager.ensure_shelf_access(shelf, current_user, user)
        logs = await self.log_repo.get_user_progress_logs(user.id)
        return logs