from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.library.progress.dependencies.progress import get_progress_log_manager, get_reading_period_manager
from src.backend.library.progress.managers.progress_logs import ProgressLogManager
from src.backend.library.progress.managers.reading_period import ReadingPeriodManager
from src.backend.library.progress.schemas.progress import GetProgressLog, GetReadingPeriod
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{user_id}",
    tags=["user_progress"],
)

@cbv(router)
class UserProgressRouter:
    """CBV router for fetching a user's own progress logs and reading periods."""

    user: User = Depends(get_current_user)
    progress_log_manager: ProgressLogManager = Depends(get_progress_log_manager)
    reading_period_manager: ReadingPeriodManager = Depends(get_reading_period_manager)

    @router.get(
        "/progress",
        summary="getting user's progress logs",
        response_model=list[GetProgressLog],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_my_progress_logs(
            self,
    ):
        """Fetches the current user's progress logs."""
        result = await self.progress_log_manager.get_my_progress_logs(self.user)
        return result

    @router.get(
        "/periods",
        summary="getting user's reading periods",
        response_model=list[GetReadingPeriod],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_my_reading_periods(
            self,
    ):
        """Fetches the current user's reading periods."""
        result = await self.reading_period_manager.get_my_reading_periods(self.user)
        return result