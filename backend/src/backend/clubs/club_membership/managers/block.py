from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.exceptions import ClubModeratorError, MemberBlockedError
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.identity.users.managers import UserManager
from src.backend.identity.users.repository import UserRepository
from src.backend.clubs.club_membership.exceptions import MemberAlreadyBlockedError, ClubBlockNotFoundError, \
    ClubOwnerError
from src.backend.clubs.club_membership.models import ClubBlocked
from src.backend.clubs.club_membership.repository.block import ClubBlockedRepository
from src.backend.clubs.club_membership.schemas import CreateBlockedMember, MemberRole
from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_owner
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User


class ClubBlockedManager:
    """Handles business logic for blocking and unblocking club members."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.blocked_member_repo = ClubBlockedRepository(session)
        self.membership_repo = ClubMembershipRepository(session)
        self.user_manager = UserManager(session)


    async def block_user(
            self,
            user: User,
            club: Club,
            request: CreateBlockedMember,
    ) -> ClubBlocked:
        """Blocks a user from the club and removes any existing membership; requires owner or moderator role.

        Args:
            user: Authenticated user performing the block.
            club: Club the target user is being blocked from.
            request: CreateBlockedMember payload with the target user's ID.

        Returns:
            Newly created ClubBlocked instance.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            UserNotFoundError: When the target user does not exist.
            ClubOwnerError: When the target user is the club owner.
            ClubModeratorError: When the target user is a moderator and the caller is not the club owner.
            MemberAlreadyBlockedError: When the target user is already blocked.
        """
        is_owner_or_moderator(club, user.id)
        club_owner = is_club_owner(club, user.id)

        target_user = await self.user_manager.get_user_by_id(request.user_id)
        membership = await self.membership_repo.get_user_club_membership(club, target_user)

        if membership:
            if membership.role == MemberRole.club_owner:
                raise ClubOwnerError("Club owner can not be blocked")
            if membership.role == MemberRole.club_moderator and not club_owner:
                raise ClubModeratorError("Only club owner can block moderator")

        try:
            result = await self.blocked_member_repo.block_user(
                club_id=club.id,
                user_id=request.user_id,
            )
        except IntegrityError:
            raise MemberAlreadyBlockedError("User already blocked")

        if membership:
            await self.membership_repo.delete_membership(membership)

        await self.session.commit()
        return result

    async def delete_block(
            self,
            user: User,
            club: Club,
            block: ClubBlocked
    ) -> None:
        """Removes a block on a club member; requires owner or moderator role.

        Args:
            user: Authenticated user performing the action.
            club: Club the block belongs to.
            block: ClubBlocked instance to remove.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
        """
        is_owner_or_moderator(club, user.id)

        await self.blocked_member_repo.delete_block(
            block=block
        )
        await self.session.commit()

    async def get_club_blocked(
            self,
            club: Club,
    ) -> list[ClubBlocked]:
        """Lists all users blocked from a club.

        Args:
            club: Club whose blocked users are listed.

        Returns:
            List of ClubBlocked instances.
        """
        result = await self.blocked_member_repo.get_club_blocked(
            club_id=club.id,
        )
        return result

    async def get_block_by_id(
            self,
            block_id: int
    ) -> ClubBlocked:
        """Fetches a club block record by ID, raising an error if not found.

        Args:
            block_id: ID of the block record.

        Returns:
            ClubBlocked instance.

        Raises:
            ClubBlockNotFoundError: When no block with the given ID exists.
        """
        result = await self.blocked_member_repo.get_block_by_id(
            block_id=block_id,
        )
        if not result:
            raise ClubBlockNotFoundError("Club block not found")
        return result

    async def is_blocked_member(
            self,
            club_id: int,
            user_id: int
    ) -> None:
        """Raises if the given user is blocked from the given club.

        Args:
            club_id: ID of the club to check.
            user_id: ID of the user to check.

        Raises:
            MemberBlockedError: When the user is blocked from the club.
        """
        result = await self.blocked_member_repo.is_blocked_member(
            club_id=club_id,
            user_id=user_id,
        )
        if result:
            raise MemberBlockedError("User blocked by club")