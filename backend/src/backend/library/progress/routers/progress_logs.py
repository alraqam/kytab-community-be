from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.users.dependencies import get_user_or_404
from src.backend.library.progress.dependencies import get_progress_log_manager
from src.backend.library.shelf.dependencies import get_shelf_item_or_404, get_shelf_or_404
from src.backend.library.shelf.models import Shelf, ShelfItem
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.library.progress.dependencies import get_reading_period_or_404, get_progress_log_or_404
from src.backend.library.progress.managers.progress_logs import ProgressLogManager
from src.backend.library.progress.models import ReadingPeriod, ProgressLog
from src.backend.library.progress.schemas import LogProgressSchema, GetProgressLog

router = APIRouter(
    prefix="/{reading_period_id}/progress",
    tags=["progress"],
)

@cbv(router)
class ProgressLogRouter:
    """CBV router for logging and retrieving a user's reading progress within a reading period."""

    shelf: Shelf = Depends(get_shelf_or_404)
    shelf_item: ShelfItem = Depends(get_shelf_item_or_404)
    reading_period: ReadingPeriod = Depends(get_reading_period_or_404)
    user: User = Depends(get_current_user)
    progress_log_manager: ProgressLogManager = Depends(get_progress_log_manager)

    @router.post(
        "/",
        summary="logging progress",
        response_model=GetProgressLog,
    )
    async def log_progress(
            self,
            request: LogProgressSchema,
    ):
        """Logs the current user's reading progress for today."""
        result = await self.progress_log_manager.log_progress(self.user, self.reading_period, request)
        return result

    @router.put(
        "/{progress_log_id}",
        summary="updating today's progress",
    )
    async def update_today_progress(
            self,
            request: LogProgressSchema,
            log: ProgressLog = Depends(get_progress_log_or_404),
    ):
        """Updates the current user's progress log for today."""
        await self.progress_log_manager.update_today_progress(self.user, log, request)

    @router.get(
        "/today",
        summary="getting user's today progress log",
        response_model=GetProgressLog,
    )
    async def get_user_today_progress_log(
            self,
    ):
        """Fetches the current user's progress log for today."""
        result = await self.progress_log_manager.get_user_today_progress_log(self.user, self.reading_period)
        return result

    @router.get(
        "/{progress_log_id}",
        summary="getting progress log by id",
    )
    async def get_progress_log_by_id(
            self,
            log: ProgressLog = Depends(get_progress_log_or_404),
    ):
        """Fetches a progress log by ID."""
        return log

    @router.get(
        "/user/{user_id}",
        summary="getting user's progress logs",
        response_model=list[GetProgressLog]
    )
    async def get_user_reading_periods(
            self,
            user: User = Depends(get_user_or_404),
    ):
        """Fetches a user's progress logs, subject to shelf visibility rules."""
        result = await self.progress_log_manager.get_users_progress_logs(user, self.user, self.shelf)
        return result
