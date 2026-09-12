import math
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.models import Shelf
from src.backend.library.progress.exceptions import ActiveReadingPeriodError
from src.backend.library.progress.managers.reading_period import ReadingPeriodManager
from src.backend.identity.auth.models import User
from src.backend.library.progress.dependencies import is_log_owner
from src.backend.library.progress.exceptions import ProgressLogNotFound, LogDateError, NoTotalPagesError, \
    NoProgressLoggedError
from src.backend.library.progress.models import ReadingPeriod, ProgressLog
from src.backend.library.progress.repositories.progress_logs import ProgressLogRepository
from src.backend.library.progress.schemas import LogProgressSchema, GetReadingPace


class ProgressLogManager:
    """Handles business logic for logging and retrieving a user's daily reading progress."""

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
        """Logs a user's reading progress for today, creating or updating today's entry.

        If the total pages read reaches the edition's page count, the reading period
        is automatically marked as finished.

        Args:
            user: User logging their progress.
            reading_period: ReadingPeriod being logged against.
            request: LogProgressSchema payload with pages read and an optional note.

        Returns:
            The created or updated ProgressLog for today.

        Raises:
            ActiveReadingPeriodError: When the reading period has already finished.
            ShelfNotFoundError: When the shelf backing the reading period, or the
                user's "currently reading" shelf, cannot be found while marking the
                period as finished.
            IsNotShelfOwnerError: When the user does not own the shelf backing the
                reading period while marking it as finished.
        """
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

        edition = await self.reading_period_manager.get_edition_by_reading_period(reading_period)
        total_pages = edition.pages_count if edition else None

        if total_pages:
            total_read = await self.log_repo.get_total_pages_read(user.id, reading_period.id)
            if total_read >= total_pages:
                await self.reading_period_manager.set_finishing_date(user, reading_period)

        await self.session.commit()
        return await self.log_repo.get_progress_log_by_id(result.id)

    async def update_today_progress(
            self,
            user: User,
            log: ProgressLog,
            request: LogProgressSchema
    ) -> None:
        """Updates today's progress log for the owning user, adding pages and replacing the note.

        Args:
            user: User expected to own the progress log.
            log: ProgressLog instance to update.
            request: LogProgressSchema payload with pages read and an optional note.

        Raises:
            IsNotProgressLogOwnerError: When the user does not own the progress log.
            LogDateError: When the log is not from today.
        """
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
        """Fetches a progress log by ID.

        Args:
            log_id: ID of the progress log to fetch.

        Returns:
            Matching ProgressLog instance.

        Raises:
            ProgressLogNotFound: When no progress log matches the ID.
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
        """Fetches the user's progress log for today within a reading period.

        Args:
            user: User whose today log is fetched.
            reading_period: ReadingPeriod to look up the log within.

        Returns:
            Matching ProgressLog instance.

        Raises:
            ProgressLogNotFound: When no progress log exists for the user today.
        """
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
        """Lists all progress logs created by the given user.

        Args:
            user: User whose progress logs are listed.

        Returns:
            List of matching ProgressLog instances.
        """
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
        """Lists a user's progress logs, enforcing shelf visibility rules for the requester.

        Args:
            user: User whose progress logs are listed.
            current_user: User making the request.
            shelf: Shelf used to check visibility access.

        Returns:
            List of matching ProgressLog instances.

        Raises:
            PrivateShelfError: When the current user is not permitted to view the shelf.
        """
        await self.shelf_manager.ensure_shelf_access(shelf, current_user, user)
        logs = await self.log_repo.get_user_progress_logs(user.id)
        return logs

    async def estimate_reading_pace(
            self,
            user: User,
            reading_period: ReadingPeriod,
    ) -> GetReadingPace:
        """Estimates the user's reading pace and projects a finish date for a current read.

        Pace is the average pages read per day since the reading period started.

        Args:
            user: User the reading period belongs to.
            reading_period: ReadingPeriod to estimate the pace for.

        Returns:
            GetReadingPace with pages per day, pages remaining, and a projected finish date.

        Raises:
            ActiveReadingPeriodError: When the reading period has already finished.
            NoTotalPagesError: When the edition has no page count to project against.
            NoProgressLoggedError: When no progress has been logged yet for the period.
        """
        if reading_period.finished_at is not None:
            raise ActiveReadingPeriodError("Reading period already finished")

        edition = await self.reading_period_manager.get_edition_by_reading_period(reading_period)
        total_pages = edition.pages_count if edition else None
        if not total_pages:
            raise NoTotalPagesError("Book has no page count")

        total_read = await self.log_repo.get_total_pages_read(user.id, reading_period.id)
        if not total_read:
            raise NoProgressLoggedError("No progress logged yet")

        elapsed_days = (date.today() - reading_period.started_at.date()).days + 1
        pages_per_day = total_read / max(elapsed_days, 1)

        pages_remaining = max(total_pages - total_read, 0)
        days_remaining = math.ceil(pages_remaining / pages_per_day)
        projected_finish_date = date.today() + timedelta(days=days_remaining)

        return GetReadingPace(
            pages_per_day=round(pages_per_day, 2),
            pages_remaining=pages_remaining,
            projected_finish_date=projected_finish_date,
        )