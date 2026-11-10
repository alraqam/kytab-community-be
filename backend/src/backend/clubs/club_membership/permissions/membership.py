
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.exceptions.membership import IsNotClubOwnerError, NotClubMemberError, \
    ClubAccessDeniedError
from src.backend.clubs.club_membership.repository.invitation import ClubInvitationRepository
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.clubs.club_membership.schemas.membership import MemberRole
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.clubs.schemas.club import ClubTypes
from src.backend.identity.auth.models.auth import User
from src.backend.identity.auth.schemas.auth import UserRoleEnum
from src.backend.identity.users.exceptions.user import PermissionDeniedError
from src.backend.trust_safety.audit_log.managers.audit_log import AuditLogManager
from src.backend.trust_safety.audit_log.schemas.audit_log import AuditLogAction


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

def is_club_owner(club: Club, user: User) -> bool:
    """Checks that the user is the club's owner.

    Args:
        club: Club instance to check ownership of.
        user: User to verify.

    Returns:
        True if the user is the club owner.

    Raises:
        IsNotClubOwnerError: When the user is not the club owner.
    """
    if user.id != club.owner_id:
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
        NotClubMemberError: When the user is not a member of a public club.
        ClubAccessDeniedError: When the user is not a member of a private or secret
            club; raised instead of NotClubMemberError so the response is
            indistinguishable from the club not existing.
    """
    repo =  ClubMembershipRepository(session)
    membership = await repo.get_user_club_membership(club, user)
    if not membership:
        if club.club_type == ClubTypes.public:
            raise NotClubMemberError("Not club member")
        raise ClubAccessDeniedError("Club not found")
    return True

def has_staff_club_access(club: Club, user: User) -> bool:
    """Returns whether a user has platform-staff access to a club without being a member.

    Admins have access to every club. A platform moderator has access only to the clubs
    assigned to them (`club.platform_manager_id`). Nobody else has staff access.

    Args:
        club: Club to check.
        user: User to check.

    Returns:
        True if the user is an admin, or the platform moderator assigned to the club.
    """
    if user.role == UserRoleEnum.admin:
        return True
    return user.role == UserRoleEnum.moderator and club.platform_manager_id == user.id

def ensure_staff_club_access(club: Club, user: User) -> None:
    """Raises unless the user has platform-staff access to the club (see `has_staff_club_access`).

    Args:
        club: Club to check.
        user: Staff member acting on the club.

    Raises:
        PermissionDeniedError: When a platform moderator acts on a club not assigned to them.
    """
    if not has_staff_club_access(club, user):
        raise PermissionDeniedError("This club is not assigned to you")

async def can_view_club(
        club: Club,
        user: User,
        session: AsyncSession,
        viewed: str,
) -> bool:
    """Verifies that the user may read a club's content.

    Admins may read the content of any club, and platform moderators the content of the
    clubs assigned to them, whatever the privacy tier (public, private, or secret),
    without being a member. Each such access by a non-member staff user is recorded in the audit log
    (`club_content_viewed`), so staff access to club content can be reviewed.
    Everyone else must be a member. Use this for read-only operations only; writes
    (posting, reacting, voting, RSVPs, progress) must keep using `is_club_member`.

    Args:
        club: Club instance with members relationship loaded.
        user: User to check.
        session: Async SQLAlchemy session used to query membership and write the audit entry.
        viewed: Short description of what is being viewed (e.g. "posts in thread 12"),
            recorded as the audit entry's details.

    Returns:
        True if the user may view the club's content.

    Raises:
        NotClubMemberError: When a non-staff user is not a member of a public club.
        ClubAccessDeniedError: When a non-staff user is not a member of a private or
            secret club.
    """
    if has_staff_club_access(club, user):
        if get_user_role_in_club(club, user.id) is None:
            await AuditLogManager(session).log(
                actor=user,
                action=AuditLogAction.club_content_viewed,
                object_type="club",
                object_id=club.id,
                details=f"Viewed {viewed} ({club.club_type} club)",
            )
        return True
    return await is_club_member(club, user, session)

async def can_preview_club(
        club: Club,
        user: User,
        session: AsyncSession,
) -> bool:
    """Verifies that the user may see a club's pre-join preview (FR-CLB-04).

    - Members, admins, and the club's assigned platform moderator may always preview.
    - Archived clubs are hidden from everyone else.
    - Public and Private clubs are listed in the directory, so any signed-in user may preview them.
    - Secret clubs may only be previewed by users holding a pending, unexpired invitation;
      for anyone else the club is indistinguishable from not existing.

    Args:
        club: Club instance with members relationship loaded.
        user: User requesting the preview.
        session: Async SQLAlchemy session used to look up invitations.

    Returns:
        True if the user may preview the club.

    Raises:
        ClubAccessDeniedError: When the user may not preview the club.
    """
    if has_staff_club_access(club, user) or get_user_role_in_club(club, user.id) is not None:
        return True
    if club.is_archived:
        raise ClubAccessDeniedError("Club not found")
    if club.club_type != ClubTypes.secret:
        return True

    invitations = await ClubInvitationRepository(session).get_pending_invitation(club.id, user.id)
    now = datetime.now()
    if any(invitation.expires_at > now for invitation in invitations):
        return True
    raise ClubAccessDeniedError("Club not found")

def bypasses_spoiler_gate(club: Club, user: User) -> bool:
    """Returns whether milestone spoiler gating should be skipped for this user.

    Staff with access to the club (admins, or its assigned platform moderator) who are
    not members see everything so they can moderate it.
    Staff who are members keep the normal spoiler experience for their own reading.

    Args:
        club: Club instance with members relationship loaded.
        user: User requesting content.

    Returns:
        True if the user has staff access to the club and is not a member of it.
    """
    return has_staff_club_access(club, user) and get_user_role_in_club(club, user.id) is None