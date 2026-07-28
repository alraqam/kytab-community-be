from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.email import create_club_invite_token, send_club_invite_email, \
    decode_club_invite_token
from src.backend.clubs.club_membership.managers.block import ClubBlockedManager
from src.backend.identity.auth.exceptions import InvalidTokenError
from src.backend.clubs.club_membership.exceptions import UnavailableInvitationError, InvitationNotFoundError, \
    DuplicateInvitationError
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.models import ClubInvitation
from src.backend.clubs.club_membership.repository.invitation import ClubInvitationRepository
from src.backend.clubs.club_membership.schemas import SendInvitation, InvitationStatus, InvitationEmail
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager



class ClubInvitationManager:
    """Handles business logic for club invitation lifecycle."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.club_manager = ClubManager(session)
        self.user_manager = UserManager(session)
        self.membership_manager = ClubMembershipManager(session)
        self.club_blocked_manager = ClubBlockedManager(session)
        self.invitation_repo = ClubInvitationRepository(session)

    async def send_invitation(
            self,
            user: User,
            request: SendInvitation
    ) -> ClubInvitation:
        """Sends a club invitation to a user; requires owner or moderator role.

        Args:
            user: Authenticated user sending the invitation.
            request: SendInvitation payload with club_id and target user_id.

        Returns:
            Newly created ClubInvitation instance.

        Raises:
            IsNotClubOwnerError: When the sender is not an owner or moderator.
            AlreadyClubMemberError: When the target user is already a member.
        """
        club = await self.club_manager.get_club_by_id(request.club_id)
        is_owner_or_moderator(club, user.id)

        invited_user = await self.user_manager.get_user_by_id(request.user_id)

        membership = await self.membership_manager.get_user_club_membership(club, invited_user)
        await self.club_blocked_manager.is_blocked_member(club.id, invited_user .id)

        existing = await self.invitation_repo.get_pending_invitation(club.id, invited_user.id)
        if existing:
            raise DuplicateInvitationError("Invitation already pending")

        invitation = await self.invitation_repo.create_invitation(
            club_id=club.id,
            invited_by_id=user.id,
            invited_user_id=invited_user.id
        )

        await self.session.commit()
        return invitation


    async def send_invitation_email(
            self,
            user: User,
            request: SendInvitation
    ) -> ClubInvitation:
        club = await self.club_manager.get_club_by_id(request.club_id)
        is_owner_or_moderator(club, user.id)

        invited_user = await self.user_manager.get_user_by_id(request.user_id)

        membership = await self.membership_manager.get_user_club_membership(club, invited_user)
        await self.club_blocked_manager.is_blocked_member(club.id, invited_user.id)

        existing = await self.invitation_repo.get_pending_invitation(club.id, invited_user.id)
        if existing:
            raise DuplicateInvitationError("Invitation already pending")

        invitation = await self.invitation_repo.create_invitation(
            club_id=club.id,
            invited_by_id=user.id,
            invited_user_id=invited_user.id
        )
        token = create_club_invite_token(invitation)
        await send_club_invite_email(user.email, token)

        await self.session.commit()
        return invitation

    async def get_invitation_email(
            self,
            token: str
    ):
        invitation_id = await decode_club_invite_token(token)
        invitation = await self.invitation_repo.get_invitation_by_id(invitation_id)
        if not invitation:
            raise InvalidTokenError("Invitation not found")

        if invitation.status != InvitationStatus.pending:
            raise InvalidTokenError("Invitation is no longer valid")

        return invitation

    async def accept_invitation(
            self,
            invitation: ClubInvitation
    ) -> None:
        """Accepts a pending invitation and adds the invited user to the club.

        Args:
            invitation: ClubInvitation instance to accept.

        Raises:
            UnavailableInvitationError: When the invitation is not pending or has expired.
        """
        if invitation.status != InvitationStatus.pending or invitation.expires_at <= datetime.now():
            raise UnavailableInvitationError("Invitation is unavailable")

        await self.invitation_repo.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.accepted,
        )
        user = await self.user_manager.get_user_by_id(invitation.invited_user_id)
        club = await self.club_manager.get_club_by_id(invitation.club_id)
        await self.membership_manager.join_club(user, club)

        await self.session.commit()

    async def decline_invitation(
            self,
            invitation: ClubInvitation
    ) -> None:
        """Declines a pending invitation.

        Args:
            invitation: ClubInvitation instance to decline.

        Raises:
            UnavailableInvitationError: When the invitation is not pending or has expired.
        """
        if invitation.status != InvitationStatus.pending or invitation.expires_at <= datetime.now():
            raise UnavailableInvitationError("Invitation is unavailable")

        await self.invitation_repo.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.declined,
        )
        await self.session.commit()

    async def get_invitation_by_id(
            self,
            invitation_id: int
    ) -> ClubInvitation:
        """Fetches an invitation by ID, raising an error if not found.

        Args:
            invitation_id: ID of the invitation.

        Returns:
            ClubInvitation instance.

        Raises:
            InvitationNotFoundError: When no invitation with the given ID exists.
        """
        invitation = await self.invitation_repo.get_invitation_by_id(invitation_id)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")
        return invitation

    async def get_user_invitations(
            self,
            user: User
    ) -> list[ClubInvitation]:
        """Returns all pending, non-expired invitations for the given user.

        Args:
            user: Authenticated user whose invitations are listed.

        Returns:
            List of pending ClubInvitation instances.
        """
        invitations = await self.invitation_repo.get_user_invitations(user.id)
        return invitations