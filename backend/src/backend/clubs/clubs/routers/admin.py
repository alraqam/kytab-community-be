from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies.club import get_club_manager, get_club_or_404
from src.backend.clubs.clubs.filters.club import ClubFilter
from src.backend.clubs.clubs.managers.club import ClubManager
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.clubs.schemas.club import GetAdminClub, to_get_admin_club
from src.backend.core.dependencies import get_storage_service
from src.backend.core.storage import StorageService
from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import is_staff
from src.backend.trust_safety.audit_log.decorators.audit import audit_action
from src.backend.trust_safety.audit_log.schemas.audit_log import AuditLogAction
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/admin/clubs",
    tags=["admin"]
)

@cbv(router)
class ClubAdminRouter:
    """CBV router for platform staff (admins and platform moderators) to manage clubs: archiving (blocking), unarchiving, and listing."""

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
            club: Club = Depends(get_club_or_404),
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
            club: Club = Depends(get_club_or_404),
    ):
        """Unarchives a club."""
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
        """Lists all clubs, optionally filtered and sorted."""
        result = await self.manager.get_all_clubs(filters)
        return [to_get_admin_club(club, self.storage.presigned_url(club.cover)) for club in result]

    @router.get(
        "/{club_id}",
        summary="getting club by id",
        response_model=GetAdminClub,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_club_by_id(
            self,
            club: Club = Depends(get_club_or_404),
    ):
        """Fetches a single club by ID."""
        return to_get_admin_club(club, self.storage.presigned_url(club.cover))