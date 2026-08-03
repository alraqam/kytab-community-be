from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.email import create_club_invite_token, send_club_invite_email, \
    decode_club_invite_token
from src.backend.clubs.club_membership.managers.block import ClubBlockedManager
from src.backend.identity.auth.exceptions import InvalidTokenError
from src.backend.clubs.club_membership.exceptions import UnavailableInvitationError, InvitationNotFoundError, \
    DuplicateInvitationError, InviteeEmailDisabledError
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.models import ClubInvitation
from src.backend.clubs.club_membership.repository.invitation import ClubInvitationRepository
from src.backend.clubs.club_membership.schemas import SendInvitation, InvitationStatus, InvitationEmail
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType



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
        self.notification_manager = NotificationManager(session)

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

        await self.notification_manager.create_notification(
            user_id=invited_user.id,
            category=NotificationCategory.club_invite,
            title=f"You've been invited to join {club.name}",
            body=f"{user.username} invited you to join {club.name}",
            object_type=NotificationObjectType.invitation,
            object_id=invitation.id,
            club_id=club.id,
        )
        return invitation


    async def send_invitation_email(
            self,
            user: User,
            request: SendInvitation
    ) -> ClubInvitation:
        """Sends a club invitation along with an invite email; requires owner or moderator role.

        Args:
            user: Authenticated user sending the invitation.
            request: SendInvitation payload with club_id and target user_id.

        Returns:
            Newly created ClubInvitation instance.

        Raises:
            IsNotClubOwnerError: When the sender is not an owner or moderator.
            AlreadyClubMemberError: When the target user is already a member.
            MemberBlockedError: When the target user is blocked from the club.
            DuplicateInvitationError: When a pending invitation already exists.
            InviteeEmailDisabledError: When the invited user does not accept email invitations.
        """
        club = await self.club_manager.get_club_by_id(request.club_id)
        is_owner_or_moderator(club, user.id)

        invited_user = await self.user_manager.get_user_by_id(request.user_id)

        membership = await self.membership_manager.get_user_club_membership(club, invited_user)
        await self.club_blocked_manager.is_blocked_member(club.id, invited_user.id)

        existing = await self.invitation_repo.get_pending_invitation(club.id, invited_user.id)
        if existing:
            raise DuplicateInvitationError("Invitation already pending")

        preference = await self.notification_manager.get_effective_preference(
            invited_user.id, NotificationCategory.club_invite, club.id
        )
        if preference is not None and (not preference.email_enabled or preference.is_muted):
            raise InviteeEmailDisabledError("Invited user does not accept email invitations")

        invitation = await self.invitation_repo.create_invitation(
            club_id=club.id,
            invited_by_id=user.id,
            invited_user_id=invited_user.id
        )
        token = create_club_invite_token(invitation)
        send_club_invite_email.delay(invited_user.email, token)

        await self.session.commit()

        await self.notification_manager.create_notification(
            user_id=invited_user.id,
            category=NotificationCategory.club_invite,
            title=f"You've been invited to join {club.name}",
            body=f"{user.username} invited you to join {club.name}",
            object_type=NotificationObjectType.invitation,
            object_id=invitation.id,
            club_id=club.id,
        )
        return invitation

    async def get_invitation_email(
            self,
            token: str
    ):
        """Resolves a pending invitation from an invite email token.

        Args:
            token: Club invite JWT sent to the invited user by email.

        Returns:
            ClubInvitation instance referenced by the token.

        Raises:
            InvalidTokenError: When the token is invalid/expired, or the invitation is missing or no longer pending.
        """
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

        inviter = await self.user_manager.get_user_by_id(invitation.invited_by_id)
        await self.notification_manager.notify(
            inviter,
            category=NotificationCategory.general,
            title=f"{user.username} accepted your invite to {club.name}",
            object_type=NotificationObjectType.invitation,
            object_id=invitation.id,
            club_id=club.id,
        )

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