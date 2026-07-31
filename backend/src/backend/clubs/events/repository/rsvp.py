from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.events.filters import EventRSVPFilter
from src.backend.clubs.events.models import EventRSVP


@dataclass
class EventRSVPRepository:
    session: AsyncSession

    async def create_rsvp(
            self,
            event_id: int,
            user_id: int,
            response: str,
    ) -> EventRSVP:
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
        stmt = select(EventRSVP).where(EventRSVP.id == rsvp_id)
        result = await self.session.execute(stmt)
        rsvp = result.scalar_one_or_none()
        return rsvp

    async def get_event_rsvps(
            self,
            event_id: int,
            filters: EventRSVPFilter  | None = None
    ) -> list[EventRSVP]:
        stmt = select(EventRSVP).where(EventRSVP.event_id == event_id)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        rsvp = result.scalars().all()
        return rsvp

