from dataclasses import dataclass
from datetime import datetime, timezone, date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backend.clubs.events.models import ClubEvent


@dataclass
class ClubEventRepository:
    session: AsyncSession

    async def create_event(
            self,
            club_id: int,
            created_by_id: int,
            title: str,
            description: str | None,
            start_at: datetime,
            end_at: datetime,
            timezone: str,
            location_text: str | None,
            meeting_url: str | None,
    ) -> ClubEvent:
        result = ClubEvent(
            club_id=club_id,
            created_by_id=created_by_id,
            title=title,
            description=description,
            start_at=start_at,
            end_at=end_at,
            timezone=timezone,
            location_text=location_text,
            meeting_url=meeting_url,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_event(
            self,
            event: ClubEvent,
            title: str | None,
            description: str | None,
            start_at: datetime | None,
            end_at: datetime | None,
            timezone: str | None,
            location_text: str | None,
            meeting_url: str | None,
    ) -> None:
        updates = {
            "title": title,
            "description": description,
            "start_at": start_at,
            "end_at": end_at,
            "timezone": timezone,
            "location_text": location_text,
            "meeting_url": meeting_url,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(event, field, value)
        await self.session.flush()

    async def delete_event(
            self,
            event: ClubEvent
    ) -> None:
        await self.session.delete(event)
        await self.session.flush()

    async def get_event_by_id(
            self,
            event_id: int
    ) -> ClubEvent | None:
        stmt = select(ClubEvent).where(ClubEvent.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()
        return event

    async def get_club_events(
            self,
            club_id: int,
    ) -> list[ClubEvent]:
        stmt = select(ClubEvent).where(ClubEvent.club_id == club_id)
        result = await self.session.execute(stmt)
        event = result.scalars().all()
        return event

    async def get_club_future_events(
            self,
            club_id: int,
    ) -> list[ClubEvent]:
        stmt = select(ClubEvent).where(
            and_(
                ClubEvent.club_id == club_id,
                ClubEvent.start_at > datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(stmt)
        event = result.scalars().all()
        return event

    async def get_event_with_time(
            self,
            start_date: date,
    ) -> list[ClubEvent]:
        stmt = (
            select(ClubEvent)
            .where(ClubEvent.start_at == start_date)
            .options(selectinload(ClubEvent.club))
        )
        result = await self.session.execute(stmt)
        events = result.scalars().all()
        return events
