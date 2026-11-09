from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.analytics.dependencies.club_analytics import get_club_analytics_manager
from src.backend.clubs.analytics.managers.club_analytics import ClubAnalyticsManager
from src.backend.clubs.analytics.schemas.club_analytics import GetPlatformClubAnalytics
from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import is_staff
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/admin/analytics/clubs",
    tags=["admin"]
)

@cbv(router)
class ClubAnalyticsAdminRouter:
    """CBV router exposing platform-wide club analytics for admins."""

    manager: ClubAnalyticsManager = Depends(get_club_analytics_manager)
    user: User = Depends(is_staff)

    @router.get(
        "/",
        summary="getting platform-wide club analytics",
        response_model=GetPlatformClubAnalytics,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def get_platform_analytics(self):
        """Fetches platform-wide club analytics."""
        result = await self.manager.get_platform_analytics()
        return result
