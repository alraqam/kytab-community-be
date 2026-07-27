from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.managers.invitation import ClubInvitationManager
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.managers.requests import ClubJoinRequestManager
from src.backend.clubs.club_membership.models import ClubInvitation, ClubJoinRequest
from src.backend.core.dependencies import get_db


async def get_membership_manager(
        session: AsyncSession = Depends(get_db)
) -> ClubMembershipManager:
    """FastAPI dependency that provides a ClubMembershipManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        ClubMembershipManager bound to the current session.
    """
    return ClubMembershipManager(session)

async def get_invitation_manager(
        session: AsyncSession = Depends(get_db)
) -> ClubInvitationManager:
    """FastAPI dependency that provides a ClubInvitationManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        ClubInvitationManager bound to the current session.
    """
    return ClubInvitationManager(session)

async def get_invitation_or_404(
        invitation_id: int,
        manager: ClubInvitationManager = Depends(get_invitation_manager)
) ->  ClubInvitation:
    """FastAPI dependency that fetches an invitation by ID or raises if not found.

    Args:
        invitation_id: Invitation ID from the path parameter.
        manager: ClubInvitationManager injected by get_invitation_manager.

    Returns:
        ClubInvitation instance.

    Raises:
        InvitationNotFoundError: When no invitation with the given ID exists.
    """
    return await manager.get_invitation_by_id(invitation_id)


async def get_join_request_manager(
        session: AsyncSession = Depends(get_db)
) -> ClubJoinRequestManager:
    """FastAPI dependency that provides a ClubJoinRequestManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        ClubJoinRequestManager bound to the current session.
    """
    return ClubJoinRequestManager(session)

async def get_join_request_or_404(
        join_request_id: int,
        manager: ClubJoinRequestManager = Depends(get_join_request_manager)
) -> ClubJoinRequest:
    """FastAPI dependency that fetches a join request by ID or raises if not found.

    Args:
        join_request_id: Join request ID from the path parameter.
        manager: ClubJoinRequestManager injected by get_join_request_manager.

    Returns:
        ClubJoinRequest instance.

    Raises:
        JoinRequestNotFound: When no join request with the given ID exists.
    """
    return await manager.get_reqsrc.uest_by_id(join_request_id)

