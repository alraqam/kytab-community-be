from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.schemas.club import ManageClubModerators
from src.backend.clubs.club_membership.dependencies.membership import get_membership_manager
from src.backend.clubs.club_membership.filters.membership import ClubMembersFilter
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.schemas.membership import ManageMember, GetMembership
from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{club_id}/membership",
    tags=["memberships"]
)

@cbv(router)
class MembershipRouter:
    """CBV router for club membership endpoints."""

    manager: ClubMembershipManager = Depends(get_membership_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.post(
        "/",
        summary="joining club",
        response_model=GetMembership,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 404, 409),
    )
    async def join_public_club(self):
        """Joins the current user to the club as a reader."""
        result = await self.manager.join_public_club(self.user, self.club)
        return result

    @router.delete(
        "/",
        summary="leaving club",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def leave_club(self):
        """Removes the current user from the club."""
        await self.manager.leave_club(self.user, self.club)

    @router.delete(
        "/kick",
        summary="kicking club member",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def kick_member(
            self,
            request: ManageMember
    ):
        """Removes a member from the club; for owners and moderators."""
        await self.manager.kick_member(self.user, self.club, request)

    @router.get(
        "/members",
        summary="getting club members",
        response_model=list[GetMembership],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_memberships(
            self,
            filters: ClubMembersFilter = FilterDepends(ClubMembersFilter)
    ):
        """Returns all club members with optional filtering."""
        result = await self.manager.get_memberships(self.club, self.user, filters)
        return result

    @router.get(
        "/owner-moderator",
        summary="getting club owners and moderators",
        response_model=list[GetMembership],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_club_owner_moderator(
            self,
    ):
        """Returns the club's owner and moderators."""
        result = await self.manager.get_club_owner_moderator(self.club)
        return result

    @router.put(
        "/assign-moderator",
        summary="assigning club moderator",
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404, 409),
    )
    async def assign_moderator(
            self,
            request: ManageClubModerators
    ):
        """Promotes a club member to the moderator role."""
        result = await self.manager.assign_moderator(self.club, self.user, request)
        return result


    @router.put(
        "/remove-moderator",
        summary="removing club moderator",
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404, 409),
    )
    async def remove_moderator(
            self,
            request: ManageClubModerators
    ):
        """Demotes a club moderator back to the member role."""
        result = await self.manager.remove_moderator(self.club, self.user, request)
        return result