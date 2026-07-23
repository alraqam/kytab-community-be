from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.library.progress.dependencies import is_log_owner
from src.backend.library.progress.exceptions import ProgressLogNotFound, LogDateError
from src.backend.library.progress.models import ReadingPeriod, ProgressLog
from src.backend.library.progress.repositories.progress_logs import ProgressLogRepository
from src.backend.library.progress.schemas import LogProgressSchema


class ProgressLogManager:
    """Handles business logic for reading progress log operations."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.log_repo = ProgressLogRepository(session)

    async def log_progress(
            self,
            user: User,
            reading_period: ReadingPeriod,
            request: LogProgressSchema
    ) -> ProgressLog:
        existing = await self.log_repo.get_user_today_progress_log(
            user_id=user.id,
            period_id=reading_period.id,
            log_date=date.today(),
        )
        if existing:
            await self.log_repo.update_progress_log(existing, request.pages)
            result = existing
        else:
            result = await self.log_repo.create_progress_log(
                user_id=user.id,
                period_id=reading_period.id,
                pages_read=request.pages,
                log_date=date.today()
            )

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
        )
        await self.session.commit()


    async def get_progress_log_by_id(
            self,
            log_id: int,
    ) -> ProgressLog:
        """Fetches a progress log by ID, raising an error if not found.

        Args:
            log_id: ID of the progress log.

        Returns:
            ProgressLog instance.

        Raises:
            ProgressLogNotFound: When no log with the given ID exists.
        """
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


    async def get_user_progress_logs(
            self,
            user: User,
    ) -> list[ProgressLog]:
        result = await self.log_repo.get_user_progress_logs(
            user_id=user.id,
        )
        return result