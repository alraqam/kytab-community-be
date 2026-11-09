from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_membership.dependencies.membership import get_join_request_manager, get_join_request_or_404
from src.backend.clubs.club_membership.managers.requests import ClubJoinRequestManager
from src.backend.clubs.club_membership.models.membership import ClubJoinRequest
from src.backend.clubs.club_membership.schemas.membership import GetJoinRequest, SendJoinRequest
from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

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
        response_model=GetJoinRequest | None,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 404, 409),
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
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(400, 401, 403, 404, 409),
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
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(400, 401, 403, 404),
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
        response_model=list[GetJoinRequest],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_club_join_requests(
            self,
            club: Club = Depends(get_club_or_404)
    ):
        """Returns all pending, non-expired join requests for a club."""
        result = await self.manager.get_club_requests(self.user, club)
        return result