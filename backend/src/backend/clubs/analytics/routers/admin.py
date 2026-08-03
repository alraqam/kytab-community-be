from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.analytics.dependencies import get_club_analytics_manager
from src.backend.clubs.analytics.managers import ClubAnalyticsManager
from src.backend.clubs.analytics.schemas import GetPlatformClubAnalytics
from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin

router = APIRouter(
    prefix="/admin/analytics/clubs",
    tags=["admin"]
)

@cbv(router)
class ClubAnalyticsAdminRouter:
    """CBV router exposing platform-wide club analytics for admins."""

    manager: ClubAnalyticsManager = Depends(get_club_analytics_manager)
    user: User = Depends(is_admin)

    @router.get(
        "/",
        summary="getting platform-wide club analytics",
        response_model=GetPlatformClubAnalytics,
    )
    async def get_platform_analytics(self):
        """Fetches platform-wide club analytics."""
        result = await self.manager.get_platform_analytics()
        return result
