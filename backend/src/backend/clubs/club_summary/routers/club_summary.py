from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_summary.dependencies.club_summary import get_club_summary_manager
from src.backend.clubs.club_summary.managers.club_summary import ClubSummaryManager
from src.backend.clubs.club_summary.schemas.club_summary import GetClubSummary
from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

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
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_club_summary(self):
        """Fetches the club's member count, latest general post, and next upcoming event."""
        result = await self.manager.get_club_summary(self.user, self.club)
        return result
