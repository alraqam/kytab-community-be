from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.exceptions import AlreadyClubMemberError, NotClubMemberError
from src.backend.clubs.club_membership.filters import ClubMembersFilter
from src.backend.clubs.club_membership.models import ClubMembership
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.clubs.club_membership.schemas import MemberRole, ManageMember
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager


class ClubMembershipManager:
    """Handles business logic for club membership operations."""

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
        self.membership_repo = ClubMembershipRepository(session)

    async def get_user_club_membership(
            self,
            club: Club,
            user: User
    ) -> ClubMembership:
        """Returns None if the user is not a member; raises if they already are.

        Args:
            club: Club to check membership for.
            user: User to check.

        Returns:
            None when the user is not a member.

        Raises:
            AlreadyClubMemberError: When the user is already a member of the club.
        """
        membership = await self.membership_repo.get_user_club_membership(club, user)
        if membership:
            raise AlreadyClubMemberError("Already a member of this club")
        return membership

    async def join_public_club(
            self,
            user: User,
            club: Club,
    ) -> ClubMembership:
        """Adds a user to a club as a member; fails if already a member.

        Args:
            user: User to add to the club.
            club: Club to join.

        Returns:
            Newly created ClubMembership instance.

        Raises:
            AlreadyClubMemberError: When the user is already a member.
        """
        await self.get_user_club_membership(club, user)
        result = await self.membership_repo.create_membership(
            club_id=club.id,
            user_id=user.id,
            role=MemberRole.member
        )

        await self.session.commit()
        return result


    async def leave_club(
            self,
            user: User,
            club: Club,
    ) -> None:
        """Removes the user from a club; fails if they are not a member.

        Args:
            user: User leaving the club.
            club: Club to leave.

        Raises:
            NotClubMemberError: When the user is not a member of the club.
        """
        membership = await self.membership_repo.get_user_club_membership(club, user)
        if not membership:
            raise NotClubMemberError("Not a club member")
        await self.membership_repo.delete_membership(membership)
        await self.session.commit()


    async def kick_member(
            self,
            user: User,
            club: Club,
            request: ManageMember
    ) -> None:
        """Removes a member from the club; requires owner or moderator role.

        Args:
            user: Authenticated user performing the kick.
            club: Club from which the member is removed.
            request: ManageMember payload with the target member's ID.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            UserNotFoundError: When the target user does not exist.
            NotClubMemberError: When the target user is not a member.
        """
        is_owner_or_moderator(club, user.id)

        member = await self.user_manager.get_user_by_id(request.member_id)

        membership = await self.membership_repo.get_user_club_membership(club, member)
        if not membership:
            raise NotClubMemberError("Membership not found")

        await self.membership_repo.delete_membership(membership)
        await self.session.commit()


    async def get_memberships(
            self,
            club: Club,
            filters: ClubMembersFilter | None = None
    ) -> list[ClubMembership]:
        """Returns all club memberships.

        Args:
            club: Club whose members are listed.
            filters: Optional ClubMembersFilter for filtering and sorting.

        Returns:
            List of ClubMembership instances.
        """
        memberships = await self.membership_repo.get_memberships(club, filters)
        return memberships

    async def get_user_memberships(
            self,
            user: User
    ) -> list[ClubMembership]:
        """Returns all club memberships for the given user.

        Args:
            user: User whose memberships are retrieved.

        Returns:
            List of ClubMembership instances.
        """
        memberships = await self.membership_repo.get_user_memberships(user)
        return memberships

    async def get_club_owner_moderator(
            self,
            club: Club
    ) -> list[ClubMembership]:
        """Returns club's owner and moderators for the given club.

        Args:
            club: Club whose memberships are retrieved.

        Returns:
            List of ClubMembership instances.
        """
        memberships = await self.membership_repo.get_club_owner_moderator(club)
        return memberships