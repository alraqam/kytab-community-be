from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_membership.dependencies import get_club_moderation_manager
from src.backend.clubs.club_membership.managers.moderation import ClubModerationManager
from src.backend.clubs.club_membership.schemas import ClubModerationSummary
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{club_id}/moderation",
    tags=["memberships"]
)

@cbv(router)
class ClubModerationRouter:
    """CBV router exposing a club moderator's moderation dashboard summary."""

    manager: ClubModerationManager = Depends(get_club_moderation_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.get(
        "/summary",
        summary="getting club moderation summary",
        response_model=ClubModerationSummary,
    )
    async def get_moderation_summary(self):
        result = await self.manager.get_moderation_summary(self.user, self.club)
        return result
