from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.analytics.dependencies import get_club_analytics_manager
from src.backend.clubs.analytics.managers import ClubAnalyticsManager
from src.backend.clubs.analytics.schemas import ClubModerationSummary, GetClubAnalytics
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{club_id}/analytics",
    tags=["analytics"]
)

@cbv(router)
class ClubAnalyticsRouter:
    """CBV router exposing a club owner/moderator's analytics dashboard."""

    manager: ClubAnalyticsManager = Depends(get_club_analytics_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.get(
        "/moderation",
        summary="getting club moderation summary",
        response_model=ClubModerationSummary,
    )
    async def get_moderation_summary(self):
        result = await self.manager.get_moderation_summary(self.user, self.club)
        return result

    @router.get(
        "/overview",
        summary="getting club analytics overview",
        response_model=GetClubAnalytics,
    )
    async def get_club_overview(self):
        result = await self.manager.get_club_overview(self.user, self.club)
        return result
