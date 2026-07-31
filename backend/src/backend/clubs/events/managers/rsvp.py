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


class EventRSVPManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.rsvp_repo = EventRSVPRepository(session)

    async def create_rsvp(
            self,
            user: User,
            club: Club,
            event: ClubEvent,
            request: CreateEventRSVP
    ) -> EventRSVP:
        await is_club_member(club, user, self.session)

        if event.end_at <= datetime.now(timezone.utc):
            raise EventDateInPastError("Event already ended")

        response = await self.rsvp_repo.create_rsvp(
            event_id=event.id,
            user_id=user.id,
            response=request.status
        )

        await self.session.commit()
        return response

    async def get_event_rsvps(
            self,
            user: User,
            club: Club,
            event: ClubEvent,
            filters: EventRSVPFilter
    ) -> list[EventRSVP]:
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
        rsvp = await self.rsvp_repo.get_rsvp_by_id(
            rsvp_id=rsvp_id,
        )
        if not rsvp:
            raise RsvpNotFoundError("Rsvp not found")
        return rsvp