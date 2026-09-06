from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_summary.dependencies import get_club_summary_manager
from src.backend.clubs.club_summary.managers import ClubSummaryManager
from src.backend.clubs.club_summary.schemas import GetClubSummary
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{club_id}/summary",
    tags=["club_summary"]
)

@cbv(router)
class ClubSummaryRouter:
    """CBV router exposing a member-facing club activity summary."""

    manager: ClubSummaryManager = Depends(get_club_summary_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.get(
        "/",
        summary="getting club summary",
        response_model=GetClubSummary,
    )
    async def get_club_summary(self):
        """Fetches the club's member count, latest general post, and next upcoming event."""
        result = await self.manager.get_club_summary(self.user, self.club)
        return result
