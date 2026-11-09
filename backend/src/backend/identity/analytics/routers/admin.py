from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.analytics.dependencies.user_analytics import get_user_analytics_manager
from src.backend.identity.analytics.managers.user_analytics import UserAnalyticsManager
from src.backend.identity.analytics.schemas.user_analytics import GetPlatformUserAnalytics
from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import is_staff
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/admin/analytics/users",
    tags=["admin"]
)

@cbv(router)
class UserAnalyticsAdminRouter:
    """CBV router exposing platform-wide user analytics for admins."""

    manager: UserAnalyticsManager = Depends(get_user_analytics_manager)
    user: User = Depends(is_staff)

    @router.get(
        "/",
        summary="getting platform-wide user analytics",
        response_model=GetPlatformUserAnalytics,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def get_platform_analytics(self):
        """Fetches platform-wide user analytics."""
        result = await self.manager.get_platform_analytics()
        return result
