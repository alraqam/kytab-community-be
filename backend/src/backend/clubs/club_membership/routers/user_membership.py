
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_membership.dependencies import get_membership_manager
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.schemas import GetMembership
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

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
    )
    async def get_user_memberships(self):
        result = await self.membership_manager.get_user_memberships(self.user)
        return result
