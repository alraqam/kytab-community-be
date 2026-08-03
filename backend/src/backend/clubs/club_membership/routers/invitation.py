from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv

from src.backend.clubs.club_membership.schemas import InvitationEmail
from src.backend.clubs.club_membership.dependencies import get_invitation_manager, get_invitation_or_404
from src.backend.clubs.club_membership.managers.invitation import ClubInvitationManager
from src.backend.clubs.club_membership.models import ClubInvitation
from src.backend.clubs.club_membership.schemas import GetInvitation, SendInvitation
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/invitation",
    tags=["invitations"]
)

@cbv(router)
class InvitationRouter:
    """CBV router for club invitation endpoints."""

    manager: ClubInvitationManager = Depends(get_invitation_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="sending invitation",
        response_model=GetInvitation
    )
    async def send_invitation(
            self,
            request: SendInvitation
    ):
        """Sends a club invitation to a user."""
        result = await self.manager.send_invitation(self.user, request)
        return result

    @router.post(
        "/email",
        summary="sending invitation by email",
        response_model=GetInvitation
    )
    async def send_invitation_email(
            self,
            request: SendInvitation
    ):
        """Sends a club invitation along with an invite email."""
        result = await self.manager.send_invitation_email(self.user, request)
        return result

    @router.put(
        "/{invitation_id}/accept",
        summary="accepting invitation",
    )
    async def accept_invitation(
            self,
            invitation: ClubInvitation = Depends(get_invitation_or_404)
    ):
        """Accepts a pending invitation."""
        await self.manager.accept_invitation(invitation)

    @router.put(
        "/{invitation_id}/decline",
        summary="declining invitation",
    )
    async def decline_invitation(
            self,
            invitation: ClubInvitation = Depends(get_invitation_or_404)
    ):
        """Declines a pending invitation."""
        await self.manager.decline_invitation(invitation)

    @router.get(
        "/",
        summary="getting current user invitations",
        response_model=list[GetInvitation]
    )
    async def get_user_invitations(self):
        """Returns all pending, non-expired invitations for the current user."""
        result = await self.manager.get_user_invitations(self.user)
        return result

    @router.get(
        "/email",
        summary="getting invitation by email token",
        response_model=GetInvitation
    )
    async def get_invitation_email(
            self,
            token: str = Query()
    ):
        """Resolves a pending invitation from an invite email token."""
        result = await self.manager.get_invitation_email(token)
        return result