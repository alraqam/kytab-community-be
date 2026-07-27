
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.exceptions import IsNotClubOwnerError, NotClubMemberError
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.clubs.club_membership.schemas import MemberRole
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User


def get_user_role_in_club(club: Club, user_id: int) -> str | None:
    """Returns the role of a user in a club by scanning its loaded members.

    Args:
        club: Club instance with members relationship loaded.
        user_id: ID of the user to look up.

    Returns:
        Role string if the user is a member, None otherwise.
    """
    for membership in club.members:
        if membership.user_id == user_id:
            return membership.role
    return None

def is_owner_or_moderator(club: Club, user_id: int) -> bool:
    """Checks that the user holds owner or moderator role in the club.

    Args:
        club: Club instance with members relationship loaded.
        user_id: ID of the user to verify.

    Returns:
        True if the user is an owner or moderator.

    Raises:
        IsNotClubOwnerError: When the user is not an owner or moderator.
    """
    role = get_user_role_in_club(club, user_id)
    if role not in (MemberRole.club_owner, MemberRole.club_moderator):
        raise IsNotClubOwnerError("Only club owner or moderator can access")
    return True

def is_club_owner(club: Club, user_id: int) -> bool:
    """Checks that the user holds the owner role in the club.

    Args:
        club: Club instance with members relationship loaded.
        user_id: ID of the user to verify.

    Returns:
        True if the user is the club owner.

    Raises:
        IsNotClubOwnerError: When the user is not the club owner.
    """
    role = get_user_role_in_club(club, user_id)
    if role != MemberRole.club_owner:
        raise IsNotClubOwnerError("Only club owner can access")
    return True

async def is_club_member(
        club: Club,
        user: User,
        session: AsyncSession
) -> bool:
    """Verifies that the user has an active membership in the club.

    Args:
        club: Club instance.
        user: User to check.
        session: Async SQLAlchemy session used to query membership.

    Returns:
        True if the user is a member.

    Raises:
        NotClubMemberError: When the user is not a member of the club.
    """
    repo =  ClubMembershipRepository(session)
    membership = await repo.get_user_club_membership(club, user)
    if not membership:
        raise NotClubMemberError("Not club member")
    return True