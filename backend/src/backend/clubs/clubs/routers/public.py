from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies.club import get_club_manager, get_club_or_404
from src.backend.clubs.clubs.filters.club import ClubPublicFilter
from src.backend.clubs.clubs.managers.club import ClubManager
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.clubs.schemas.club import GetClub, CreateClub, UpdateClub, ManageClubModerators, to_get_club, \
    GetClubPreview
from src.backend.core.dependencies import get_storage_service
from src.backend.core.storage import StorageService
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/clubs",
)

@cbv(router)
class ClubRouter:
    """CBV router for member-facing club actions: creation, updates, archiving, listing, and ownership transfer."""

    manager: ClubManager = Depends(get_club_manager)
    storage: StorageService = Depends(get_storage_service)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating club",
        response_model=GetClub,
        tags=["club"],
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401),
    )
    async def create_club(
            self,
            request: CreateClub,
    ):
        """Creates a new club owned by the current user."""
        result = await self.manager.create_club(self.user, request)
        return to_get_club(result, self.storage.presigned_url(result.cover))

    @router.put(
        "/{club_id}",
        summary="updating club",
        tags=["club"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_club(
            self,
            request: UpdateClub,
            club: Club = Depends(get_club_or_404),
    ):
        """Updates a club's details."""
        await self.manager.update_club(self.user, club, request)

    @router.put(
        "/{club_id}/cover",
        summary="updating club cover",
        tags=["club"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_cover(
            self,
            cover: UploadFile = File(...),
            club: Club = Depends(get_club_or_404),
    ):
        """Uploads a new cover image for the club."""
        await self.manager.update_cover(self.user, club, cover)

    @router.delete(
        "/{club_id}",
        summary="archiving club",
        tags=["club"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
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
        tags=["club"],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_clubs_list(
            self,
            filters: ClubPublicFilter = FilterDepends(ClubPublicFilter)
    ):
        """Lists non-secret, non-archived clubs, optionally filtered and sorted."""
        result = await self.manager.get_clubs_list(filters)
        return [to_get_club(club, self.storage.presigned_url(club.cover)) for club in result]

    @router.put(
        "/{club_id}/transfer",
        summary="transferring club ownership",
        tags=["club"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
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

    @router.get(
        "/{club_id}/preview",
        summary="getting club preview",
        response_model=GetClubPreview,
        tags=["club"],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_club_preview(
            self,
            club: Club = Depends(get_club_or_404),
    ):
        """Returns a club's pre-join preview: name, description, member count, and current book(s).

        Public and Private clubs can be previewed by any signed-in user; Secret clubs only
        by invited users, members, and platform staff.
        """
        return await self.manager.get_club_preview(self.user, club)
