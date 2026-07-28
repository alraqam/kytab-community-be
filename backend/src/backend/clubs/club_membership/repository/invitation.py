from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.models import ClubInvitation
from src.backend.clubs.club_membership.schemas import InvitationStatus


@dataclass
class ClubInvitationRepository:
    """Data access layer for ClubInvitation model operations."""

    session: AsyncSession

    async def create_invitation(
            self,
            club_id: int,
            invited_by_id: int,
            invited_user_id: int,
    ) -> ClubInvitation:
        """Creates a new club invitation with a 14-day expiry.

        Args:
            club_id: ID of the club the invitation is for.
            invited_by_id: ID of the user sending the invitation.
            invited_user_id: ID of the user being invited.

        Returns:
            Newly created ClubInvitation instance.
        """
        result = ClubInvitation(
            club_id=club_id,
            invited_by_id=invited_by_id,
            invited_user_id=invited_user_id,
            expires_at=datetime.now() + timedelta(days=14)
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_invitation_status(
            self,
            invitation: ClubInvitation,
            status: str
    ) -> None:
        """Updates the status of an invitation and flushes the session.

        Args:
            invitation: ClubInvitation instance to update.
            status: New status string.
        """
        invitation.status = status
        self.session.add(invitation)
        await self.session.flush()

    async def get_invitation_by_id(
            self,
            invitation_id: int,
    ) -> ClubInvitation | None:
        """Fetches an invitation by its ID.

        Args:
            invitation_id: ID of the invitation.

        Returns:
            ClubInvitation instance if found, None otherwise.
        """
        stmt = select(ClubInvitation).where(ClubInvitation.id == invitation_id)
        result = await self.session.execute(stmt)
        invitation = result.scalar_one_or_none()
        return invitation

    async def get_user_invitations(
            self,
            user_id: int
    ) -> list[ClubInvitation]:
        """Returns all pending, non-expired invitations for a user.

        Args:
            user_id: ID of the invited user.

        Returns:
            List of pending ClubInvitation instances.
        """
        stmt = select(ClubInvitation).where(
            and_(
                ClubInvitation.invited_user_id == user_id,
                ClubInvitation.status == InvitationStatus.pending,
                ClubInvitation.expires_at >= datetime.now()
            ))
        result = await self.session.execute(stmt)
        invitations = result.scalars().all()
        return invitations

    async def get_pending_invitation(
            self,
            club_id: int,
            user_id: int
    ):
        stmt = select(ClubInvitation).where(
            and_(
                ClubInvitation.invited_user_id == user_id,
                ClubInvitation.status == InvitationStatus.pending,
                ClubInvitation.club_id >= club_id
            ))
        result = await self.session.execute(stmt)
        invitations = result.scalars().all()
        return invitations

