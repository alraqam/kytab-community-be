from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from backend.identity.auth.dependencies import get_current_user
from backend.identity.auth.models import User
from backend.library.progress.dependencies import get_reading_period_or_404, get_progress_log_or_404
from backend.library.progress.managers.progress_logs import ProgressLogManager
from backend.library.progress.models import ReadingPeriod, ProgressLog
from backend.library.progress.schemas import LogProgressSchema, GetProgressLog

router = APIRouter(
    prefix="/{reading_period_id}/progress",
    tags=["progress"],
)

@cbv(router)
class ProgressLogRouter:
    reading_period: ReadingPeriod = Depends(get_reading_period_or_404)
    user: User = Depends(get_current_user)
    progress_log: ProgressLogManager = Depends(get_progress_log_or_404)

    @router.post(
        "/",
        summary="logging progress",
        response_model=GetProgressLog,
    )
    async def log_progress(
            self,
            request: LogProgressSchema,
    ):
        result = await self.progress_log.log_progress(self.user, self.reading_period, request)
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
        await self.progress_log.update_today_progress(self.user, log, request)

    @router.get(
        "/{progress_log_id}",
        summary="getting progress log by id",
    )
    async def get_progress_log_by_id(
            self,
            log: ProgressLog = Depends(get_progress_log_or_404),
    ):
        return log

    @router.get(
        "/",
        summary="getting user's today progress log",
        response_model=GetProgressLog,
    )
    async def get_user_today_progress_log(
            self,
    ):
        result = await self.progress_log.get_user_today_progress_log(self.user, self.reading_period)
        return result

    @router.get(
        "/",
        summary="getting user's today progress log",
        response_model=GetProgressLog,
    )
    async def get_user_today_progress_log(
            self,
    ):
        result = await self.progress_log.get_user_today_progress_log(self.user, self.reading_period)
        return result