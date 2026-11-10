from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies.club import get_club_manager, get_managed_club_or_404, get_club_or_404
from src.backend.clubs.clubs.filters.club import ClubFilter
from src.backend.clubs.clubs.managers.club import ClubManager
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.clubs.schemas.club import GetAdminClub, to_get_admin_club, AssignPlatformManager, \
    GetPlatformManagerLoad, AssignUnassignedClubsResult
from src.backend.core.dependencies import get_storage_service
from src.backend.core.storage import StorageService
from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import is_staff, is_admin
from src.backend.trust_safety.audit_log.decorators.audit import audit_action
from src.backend.trust_safety.audit_log.schemas.audit_log import AuditLogAction
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/admin/clubs",
    tags=["admin"]
)

@cbv(router)
class ClubAdminRouter:
    """CBV router for platform staff to manage clubs: archiving (blocking), unarchiving, listing, and platform-moderator assignment.

    Admins can act on any club. Platform moderators can only act on the clubs assigned to them.
    """

    manager: ClubManager = Depends(get_club_manager)
    storage: StorageService = Depends(get_storage_service)
    user: User = Depends(is_staff)

    @router.put(
        "/{club_id}/archive",
        summary="archiving clubs",
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    @audit_action(AuditLogAction.club_archived, "club", id_from="club")
    async def archive_club(
            self,
            club: Club = Depends(get_managed_club_or_404),
    ):
        """Archives a club."""
        result = await self.manager.archive_club(club)
        return result

    @router.put(
        "/{club_id}/unarchive",
        summary="unarchiving clubs",
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    @audit_action(AuditLogAction.club_unarchived, "club", id_from="club")
    async def unarchive_club(
            self,
            club: Club = Depends(get_managed_club_or_404),
    ):
        """Unarchives a club, returning it to its previous platform moderator (or the least-loaded one if they're no longer eligible)."""
        result = await self.manager.unarchive_club(club)
        return result

    @router.get(
        "/",
        summary="getting clubs",
        response_model=list[GetAdminClub],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def get_all_clubs(
            self,
            filters: ClubFilter = FilterDepends(ClubFilter)
    ):
        """Lists clubs, optionally filtered and sorted. Platform moderators only see clubs assigned to them."""
        result = await self.manager.get_all_clubs(filters, self.user)
        return [to_get_admin_club(club, self.storage.presigned_url(club.cover)) for club in result]

    @router.get(
        "/assigned",
        summary="getting my assigned active clubs",
        response_model=list[GetAdminClub],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def get_assigned_clubs(self):
        """Lists the active (non-archived) clubs assigned to the current platform moderator."""
        result = await self.manager.get_assigned_clubs(self.user)
        return [to_get_admin_club(club, self.storage.presigned_url(club.cover)) for club in result]

    @router.get(
        "/managers",
        summary="getting platform moderators with their club counts",
        dependencies=[Depends(is_admin)],
        response_model=list[GetPlatformManagerLoad],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def get_platform_manager_loads(self):
        """Lists every active platform moderator with their number of active clubs. Admin-only."""
        return await self.manager.get_platform_manager_loads()

    @router.post(
        "/assign-unassigned",
        summary="assigning clubs without a platform moderator",
        dependencies=[Depends(is_admin)],
        response_model=AssignUnassignedClubsResult,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def assign_unassigned_clubs(self):
        """Assigns every active club that has no platform moderator (e.g. created while there were none). Admin-only."""
        assigned = await self.manager.assign_unassigned_clubs()
        return AssignUnassignedClubsResult(assigned=assigned)

    @router.put(
        "/{club_id}/manager",
        summary="assigning a club to a platform moderator",
        dependencies=[Depends(is_admin)],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(400, 401, 403, 404),
    )
    @audit_action(
        AuditLogAction.club_manager_assigned,
        "club",
        id_from="club",
        details_from=lambda request, **_: f"Assigned to platform moderator {request.user_id}",
    )
    async def set_platform_manager(
            self,
            request: AssignPlatformManager,
            club: Club = Depends(get_club_or_404),
    ):
        """Manually assigns a club to a platform moderator. Admin-only. The club counts toward that moderator's load."""
        await self.manager.set_platform_manager(club, request.user_id)

    @router.get(
        "/{club_id}",
        summary="getting club by id",
        response_model=GetAdminClub,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_club_by_id(
            self,
            club: Club = Depends(get_managed_club_or_404),
    ):
        """Fetches a single club by ID. Platform moderators can only fetch clubs assigned to them."""
        return to_get_admin_club(club, self.storage.presigned_url(club.cover))
