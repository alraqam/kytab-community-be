from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.managers.block import ClubBlockedManager
from src.backend.clubs.club_membership.exceptions import UnavailableRequestError, JoinRequestNotFound
from src.backend.clubs.club_membership.models import ClubJoinRequest
from src.backend.clubs.club_membership.repository.requests import ClubJoinRequestRepository
from src.backend.clubs.club_membership.schemas import SendJoinRequest, JoinRequestStatus
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.schemas import ClubTypes
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager


class ClubJoinRequestManager:
    """Handles business logic for club join request lifecycle."""

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
        self.request_repo = ClubJoinRequestRepository(session)

    async def send_join_request(
            self,
            user: User,
            request: SendJoinRequest
    ) -> ClubJoinRequest | None:
        """Sends a join request to a private club, or joins directly if the club is public.

        Args:
            user: User requesting to join.
            request: SendJoinRequest payload with the target club_id.

        Returns:
            ClubJoinRequest instance for private clubs; None if the club is public (direct join).
        """
        club = await self.club_manager.get_club_by_id(request.club_id)
        membership = await self.membership_manager.get_user_club_membership(club, user)
        await self.club_blocked_manager.is_blocked_member(club.id, user.id)

        if club.club_type == ClubTypes.public:
            await self.membership_manager.join_public_club(user, club)
            return None

        join_request = await self.request_repo.create_request(
            club_id=club.id,
            user_id=user.id,
        )

        await self.session.commit()
        return join_request

    async def accept_join_request(
            self,
            user: User,
            join_request: ClubJoinRequest
    ) -> None:
        """Accepts a pending join request and adds the requester to the club.

        Args:
            user: Club owner or moderator accepting the request.
            join_request: ClubJoinRequest instance to accept.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            UnavailableRequestError: When the request is not pending or has expired.
        """
        club = await self.club_manager.get_club_by_id(join_request.club_id)
        is_owner_or_moderator(club, user.id)

        if join_request.status != JoinRequestStatus.pending or join_request.expires_at <= datetime.now():
            raise UnavailableRequestError("Join request is unavailable")

        await self.request_repo.update_request_status(
            request=join_request,
            status=JoinRequestStatus.accepted,
        )
        member = await self.user_manager.get_user_by_id(join_request.user_id)
        await self.membership_manager.join_club(member, club)
        await self.session.commit()

    async def reject_join_request(
            self,
            user: User,
            join_request: ClubJoinRequest
    ) -> None:
        """Rejects a pending join request; requires owner or moderator role.

        Args:
            user: Club owner or moderator rejecting the request.
            join_request: ClubJoinRequest instance to reject.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
            UnavailableRequestError: When the request is not pending or has expired.
        """
        club = await self.club_manager.get_club_by_id(join_request.club_id)
        is_owner_or_moderator(club, user.id)

        if join_request.status != JoinRequestStatus.pending or join_request.expires_at <= datetime.now():
            raise UnavailableRequestError("Join request is unavailable")

        await self.request_repo.update_request_status(
            request=join_request,
            status=JoinRequestStatus.rejected,
        )
        await self.session.commit()

    async def get_request_by_id(
            self,
            request_id: int
    ) -> ClubJoinRequest:
        """Fetches a join request by ID, raising an error if not found.

        Args:
            request_id: ID of the join request.

        Returns:
            ClubJoinRequest instance.

        Raises:
            JoinRequestNotFound: When no request with the given ID exists.
        """
        join_request = await self.request_repo.get_request_by_id(request_id)
        if not join_request:
            raise JoinRequestNotFound("Join request not found")
        return join_request

    async def get_club_requests(
            self,
            user: User,
            club: Club
    ) -> list[ClubJoinRequest]:
        """Returns all pending, non-expired join requests for a club; requires owner or moderator.

        Args:
            user: Authenticated user requesting the list.
            club: Club whose join requests are listed.

        Returns:
            List of pending ClubJoinRequest instances.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator.
        """
        is_owner_or_moderator(club, user.id)
        requests = await self.request_repo.get_club_requests(club.id)
        return requests