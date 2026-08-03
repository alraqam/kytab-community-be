from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.analytics.dependencies import get_user_analytics_manager
from src.backend.identity.analytics.managers import UserAnalyticsManager
from src.backend.identity.analytics.schemas import GetUserAnalytics
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import get_user_or_404

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
    )
    async def get_my_analytics(self):
        result = await self.manager.get_user_analytics(self.user, self.user)
        return result

    @router.get(
        "/{user_id}",
        summary="getting user's analytics",
        response_model=GetUserAnalytics,
    )
    async def get_user_analytics(
            self,
            get_user: User = Depends(get_user_or_404)
    ):
        result = await self.manager.get_user_analytics(get_user, self.user)
        return result
