from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.analytics.dependencies import get_user_analytics_manager
from src.backend.identity.analytics.managers import UserAnalyticsManager
from src.backend.identity.analytics.schemas import GetPlatformUserAnalytics
from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin

router = APIRouter(
    prefix="/admin/analytics/users",
    tags=["admin"]
)

@cbv(router)
class UserAnalyticsAdminRouter:
    """CBV router exposing platform-wide user analytics for admins."""

    manager: UserAnalyticsManager = Depends(get_user_analytics_manager)
    user: User = Depends(is_admin)

    @router.get(
        "/",
        summary="getting platform-wide user analytics",
        response_model=GetPlatformUserAnalytics,
    )
    async def get_platform_analytics(self):
        result = await self.manager.get_platform_analytics()
        return result
