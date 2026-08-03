from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_manager, get_club_or_404
from src.backend.clubs.clubs.filters import ClubPublicFilter
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.schemas import GetClub, CreateClub, UpdateClub, ManageClubModerators
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/clubs",
    tags=["club"]
)

@cbv(router)
class ClubRouter:
    """CBV router for member-facing club actions: creation, updates, archiving, listing, and ownership transfer."""

    manager: ClubManager = Depends(get_club_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating club",
        response_model=GetClub,
    )
    async def create_club(
            self,
            request: CreateClub,
    ):
        """Creates a new club owned by the current user."""
        result = await self.manager.create_club(self.user, request)
        return result

    @router.put(
        "/{club_id}",
        summary="updating club",
    )
    async def update_club(
            self,
            request: UpdateClub,
            club: Club = Depends(get_club_or_404),
    ):
        """Updates a club's details."""
        await self.manager.update_club(self.user, club, request)

    @router.delete(
        "/{club_id}",
        summary="archiving club",
    )
    async def archive_club(
            self,
            club: Club = Depends(get_club_or_404),
    ):
        """Archives a club."""
        await self.manager.archive_club(club, self.user)

    @router.get(
        "/public",
        summary="getting all clubs",
        response_model=list[GetClub],
    )
    async def get_clubs_list(
            self,
            filters: ClubPublicFilter = FilterDepends(ClubPublicFilter)
    ):
        """Lists non-secret, non-archived clubs, optionally filtered and sorted."""
        result = await self.manager.get_clubs_list(filters)
        return result

    @router.put(
        "/{club_id}/transfer",
        summary="transferring club ownership",
    )
    async def transfer_ownership(
            self,
            request: ManageClubModerators,
            club: Club = Depends(get_club_or_404)
    ):
        """Transfers club ownership to another member."""
        await self.manager.transfer_ownership(
            club=club,
            user=self.user,
            request=request
        )
