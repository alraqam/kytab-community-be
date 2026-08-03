from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.events.filters import EventRSVPFilter
from src.backend.clubs.events.models import EventRSVP


@dataclass
class EventRSVPRepository:
    """Data-access layer for event RSVP persistence and queries."""

    session: AsyncSession

    async def create_rsvp(
            self,
            event_id: int,
            user_id: int,
            response: str,
    ) -> EventRSVP:
        """Inserts a new RSVP for a user on an event.

        Args:
            event_id: ID of the event being RSVP'd to.
            user_id: ID of the user submitting the RSVP.
            response: RSVP response status.

        Returns:
            Newly created EventRSVP instance.
        """
        result = EventRSVP(
            event_id=event_id,
            user_id=user_id,
            response=response,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_rsvp_by_id(
            self,
            rsvp_id: int
    ) -> EventRSVP | None:
        """Fetches a single RSVP by ID.

        Args:
            rsvp_id: ID of the RSVP to fetch.

        Returns:
            Matching EventRSVP instance, or None if not found.
        """
        stmt = select(EventRSVP).where(EventRSVP.id == rsvp_id)
        result = await self.session.execute(stmt)
        rsvp = result.scalar_one_or_none()
        return rsvp

    async def get_event_rsvps(
            self,
            event_id: int,
            filters: EventRSVPFilter  | None = None
    ) -> list[EventRSVP]:
        """Lists RSVPs for an event, optionally filtered and sorted.

        Args:
            event_id: ID of the event whose RSVPs are being listed.
            filters: EventRSVPFilter to apply, or None for no filtering.

        Returns:
            List of matching EventRSVP instances.
        """
        stmt = select(EventRSVP).where(EventRSVP.event_id == event_id)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        rsvp = result.scalars().all()
        return rsvp

