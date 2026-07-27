from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_manager, get_club_or_404
from src.backend.clubs.clubs.filters import ClubFilter
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.schemas import GetClub
from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin

router = APIRouter(
    prefix="/admin/clubs",
    tags=["admin"]
)

@cbv(router)
class ClubAdminRouter:
    manager: ClubManager = Depends(get_club_manager)
    user: User = Depends(is_admin)

    @router.put(
        "/{club_id}/archive",
        summary="archiving clubs",
    )
    async def archive_club(
            self,
            club: Club = Depends(get_club_or_404),
    ):
        result = await self.manager.archive_club(club)
        return result

    @router.put(
        "/{club_id}/unarchive",
        summary="unarchiving clubs",
    )
    async def unarchive_club(
            self,
            club: Club = Depends(get_club_or_404),
    ):
        result = await self.manager.unarchive_club(club)
        return result

    @router.get(
        "/",
        summary="getting clubs",
        response_model=list[GetClub],
    )
    async def get_all_clubs(
            self,
            filters: ClubFilter = FilterDepends(ClubFilter)
    ):
        result = await self.manager.get_all_clubs(filters)
        return result
