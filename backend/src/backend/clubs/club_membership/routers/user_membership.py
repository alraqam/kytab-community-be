
from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_membership.dependencies.membership import get_membership_manager
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.schemas.membership import GetMembership
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/membership",
    tags=["user_memberships"]
)
@cbv(router)
class UserMembershipRouter:
    """CBV router for user membership endpoints."""

    membership_manager: ClubMembershipManager = Depends(get_membership_manager)
    user: User = Depends(get_current_user)

    @router.get(
        "/",
        summary="getting club memberships",
        response_model=list[GetMembership],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_user_memberships(self):
        """Returns all club memberships for the current user."""
        result = await self.membership_manager.get_user_memberships(self.user)
        return result
