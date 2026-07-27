from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.library.progress.dependencies import get_progress_log_manager, get_reading_period_manager
from src.backend.library.progress.managers.progress_logs import ProgressLogManager
from src.backend.library.progress.managers.reading_period import ReadingPeriodManager
from src.backend.library.progress.schemas import GetProgressLog, GetReadingPeriod

router = APIRouter(
    prefix="/{user_id}",
    tags=["user_progress"],
)

@cbv(router)
class UserProgressRouter:
    user: User = Depends(get_current_user)
    progress_log_manager: ProgressLogManager = Depends(get_progress_log_manager)
    reading_period_manager: ReadingPeriodManager = Depends(get_reading_period_manager)

    @router.get(
        "/progress",
        summary="getting user's progress logs",
        response_model=list[GetProgressLog]
    )
    async def get_my_progress_logs(
            self,
    ):
        result = await self.progress_log_manager.get_my_progress_logs(self.user)
        return result

    @router.get(
        "/periods",
        summary="getting user's reading periods",
        response_model=list[GetReadingPeriod]
    )
    async def get_my_reading_periods(
            self,
    ):
        result = await self.reading_period_manager.get_my_reading_periods(self.user)
        return result