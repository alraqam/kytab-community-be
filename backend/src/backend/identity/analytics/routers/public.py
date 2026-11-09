from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.analytics.dependencies.user_analytics import get_user_analytics_manager
from src.backend.identity.analytics.managers.user_analytics import UserAnalyticsManager
from src.backend.identity.analytics.schemas.user_analytics import GetUserAnalytics
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import get_user_or_404
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/analytics/users",
    tags=["analytics"]
)

@cbv(router)
class UserAnalyticsRouter:
    """CBV router exposing personal reading analytics."""

    manager: UserAnalyticsManager = Depends(get_user_analytics_manager)
    user: User = Depends(get_current_user)

    @router.get(
        "/me",
        summary="getting current user's analytics",
        response_model=GetUserAnalytics,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_my_analytics(self):
        """Fetches the current user's reading analytics."""
        result = await self.manager.get_user_analytics(self.user, self.user)
        return result

    @router.get(
        "/{user_id}",
        summary="getting user's analytics",
        response_model=GetUserAnalytics,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_user_analytics(
            self,
            get_user: User = Depends(get_user_or_404)
    ):
        """Fetches another user's reading analytics."""
        result = await self.manager.get_user_analytics(get_user, self.user)
        return result
