from dataclasses import dataclass
from datetime import datetime, timezone, date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backend.clubs.events.models import ClubEvent


@dataclass
class ClubEventRepository:
    """Data-access layer for club event persistence and queries."""

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
        """Inserts a new club event.

        Args:
            club_id: ID of the club the event belongs to.
            created_by_id: ID of the user creating the event.
            title: Event title.
            description: Event description, or None.
            start_at: Event start time.
            end_at: Event end time.
            timezone: Timezone the event times are expressed in.
            location_text: Free-text location, or None.
            meeting_url: Online meeting URL, or None.

        Returns:
            Newly created ClubEvent instance.
        """
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
        """Updates the given fields of an event, skipping unset ones.

        Args:
            event: ClubEvent instance to update.
            title: New title, or None to leave unchanged.
            description: New description, or None to leave unchanged.
            start_at: New start time, or None to leave unchanged.
            end_at: New end time, or None to leave unchanged.
            timezone: New timezone, or None to leave unchanged.
            location_text: New location text, or None to leave unchanged.
            meeting_url: New meeting URL, or None to leave unchanged.
        """
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
        """Deletes a club event.

        Args:
            event: ClubEvent instance to delete.
        """
        await self.session.delete(event)
        await self.session.flush()

    async def get_event_by_id(
            self,
            event_id: int
    ) -> ClubEvent | None:
        """Fetches a single event by ID.

        Args:
            event_id: ID of the event to fetch.

        Returns:
            Matching ClubEvent instance, or None if not found.
        """
        stmt = select(ClubEvent).where(ClubEvent.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()
        return event

    async def get_club_events(
            self,
            club_id: int,
    ) -> list[ClubEvent]:
        """Lists all events for a club.

        Args:
            club_id: ID of the club whose events are being listed.

        Returns:
            List of matching ClubEvent instances.
        """
        stmt = select(ClubEvent).where(ClubEvent.club_id == club_id)
        result = await self.session.execute(stmt)
        event = result.scalars().all()
        return event

    async def get_club_future_events(
            self,
            club_id: int,
    ) -> list[ClubEvent]:
        """Lists a club's events that have not yet started.

        Args:
            club_id: ID of the club whose future events are being listed.

        Returns:
            List of matching ClubEvent instances.
        """
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
        """Lists events starting on the given date, with their club preloaded.

        Args:
            start_date: Date to match against event start times.

        Returns:
            List of matching ClubEvent instances.
        """
        stmt = (
            select(ClubEvent)
            .where(ClubEvent.start_at == start_date)
            .options(selectinload(ClubEvent.club))
        )
        result = await self.session.execute(stmt)
        events = result.scalars().all()
        return events
