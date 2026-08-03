from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_membership.dependencies import get_join_request_manager, get_join_request_or_404
from src.backend.clubs.club_membership.managers.requests import ClubJoinRequestManager
from src.backend.clubs.club_membership.models import ClubJoinRequest
from src.backend.clubs.club_membership.schemas import GetJoinRequest, SendJoinRequest
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/join-request",
    tags=["requests"]
)

@cbv(router)
class ClubJoinRequestRouter:
    """CBV router for club join request endpoints."""

    manager: ClubJoinRequestManager = Depends(get_join_request_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="sending join request",
        response_model=GetJoinRequest | None
    )
    async def send_join_request(
            self,
            request: SendJoinRequest
    ):
        """Sends a join request to a private club, or joins directly if public."""
        result = await self.manager.send_join_request(self.user, request)
        return result

    @router.put(
        "/{join_request_id}/accept",
        summary="accepting join request",
    )
    async def accept_join_request(
            self,
            join_request: ClubJoinRequest = Depends(get_join_request_or_404)
    ):
        """Accepts a pending join request and adds the requester to the club."""
        await self.manager.accept_join_request(self.user, join_request)

    @router.put(
        "/{join_request_id}/reject",
        summary="rejecting join request",
    )
    async def reject_join_request(
            self,
            join_request: ClubJoinRequest = Depends(get_join_request_or_404)
    ):
        """Rejects a pending join request."""
        await self.manager.reject_join_request(self.user, join_request)

    @router.get(
        "/",
        summary="getting club join request",
        response_model=list[GetJoinRequest]
    )
    async def get_club_join_requests(
            self,
            club: Club = Depends(get_club_or_404)
    ):
        """Returns all pending, non-expired join requests for a club."""
        result = await self.manager.get_club_requests(self.user, club)
        return result