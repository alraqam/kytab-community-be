from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_club_member
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.events.exceptions import EventDateInPastError, RsvpNotFoundError
from src.backend.clubs.events.filters import EventRSVPFilter
from src.backend.clubs.events.models import EventRSVP, ClubEvent
from src.backend.clubs.events.repository.rsvp import EventRSVPRepository
from src.backend.clubs.events.schemas import CreateEventRSVP
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType


class EventRSVPManager:
    """Handles business logic for RSVPs to club events: creation, retrieval, and result tallying."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """
        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.rsvp_repo = EventRSVPRepository(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)

    async def create_rsvp(
            self,
            user: User,
            club: Club,
            event: ClubEvent,
            request: CreateEventRSVP
    ) -> EventRSVP:
        """Creates an RSVP for a user on an event and notifies the event creator.

        Args:
            user: User submitting the RSVP; must be a club member.
            club: Club the event belongs to.
            event: ClubEvent being RSVP'd to.
            request: CreateEventRSVP payload with the RSVP status.

        Returns:
            Newly created EventRSVP instance.

        Raises:
            NotClubMemberError: When the user is not a member of a public club.
            ClubAccessDeniedError: When the user is not a member of a private or
                secret club (indistinguishable from the club not existing).
            EventDateInPastError: When the event has already ended.
        """
        await is_club_member(club, user, self.session)

        if event.end_at <= datetime.now(timezone.utc):
            raise EventDateInPastError("Event already ended")

        response = await self.rsvp_repo.create_rsvp(
            event_id=event.id,
            user_id=user.id,
            response=request.status
        )

        await self.session.commit()

        if event.created_by_id != user.id:
            creator = await self.user_manager.get_user_by_id(event.created_by_id)
            await self.notification_manager.notify(
                creator,
                category=NotificationCategory.general,
                title=f"{user.username} RSVP'd {request.status} to {event.title}",
                object_type=NotificationObjectType.event,
                object_id=event.id,
                club_id=club.id,
            )
        return response

    async def get_event_rsvps(
            self,
            user: User,
            club: Club,
            event: ClubEvent,
            filters: EventRSVPFilter
    ) -> list[EventRSVP]:
        """Lists RSVPs for an event matching the given filters.

        Args:
            user: User requesting the RSVPs; must be a club member.
            club: Club the event belongs to.
            event: ClubEvent whose RSVPs are being listed.
            filters: EventRSVPFilter with response status and ordering criteria.

        Returns:
            List of matching EventRSVP instances.

        Raises:
            NotClubMemberError: When the user is not a member of a public club.
            ClubAccessDeniedError: When the user is not a member of a private or
                secret club (indistinguishable from the club not existing).
        """
        await is_club_member(club, user, self.session)
        rsvps = await self.rsvp_repo.get_event_rsvps(
            event_id=event.id,
            filters=filters
        )
        return rsvps

    async def get_event_rsvp_results(
            self,
            user: User,
            club: Club,
            event: ClubEvent,
    ) -> dict:
        """Tallies RSVP responses for an event by status.

        Args:
            user: User requesting the results; must be a club member.
            club: Club the event belongs to.
            event: ClubEvent whose RSVP results are being tallied.

        Returns:
            Mapping of response status to the count of RSVPs with that status.

        Raises:
            NotClubMemberError: When the user is not a member of a public club.
            ClubAccessDeniedError: When the user is not a member of a private or
                secret club (indistinguishable from the club not existing).
        """
        await is_club_member(club, user, self.session)
        rsvps = await self.rsvp_repo.get_event_rsvps(event.id)

        rsvp_counts: dict[str, int] = {}
        for rsvp in rsvps:
            rsvp_counts[rsvp.response] = rsvp_counts.get(rsvp.response, 0) + 1

        return rsvp_counts

    async def get_rsvp_by_id(
            self,
            rsvp_id: int,
    ) -> EventRSVP:
        """Fetches a single RSVP by ID.

        Args:
            rsvp_id: ID of the RSVP to fetch.

        Returns:
            Matching EventRSVP instance.

        Raises:
            RsvpNotFoundError: When no RSVP with the given ID exists.
        """
        rsvp = await self.rsvp_repo.get_rsvp_by_id(
            rsvp_id=rsvp_id,
        )
        if not rsvp:
            raise RsvpNotFoundError("Rsvp not found")
        return rsvp