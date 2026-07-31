from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_member
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.events.exceptions import EventDateInPastError, EventNotFoundError
from src.backend.clubs.events.models import ClubEvent
from src.backend.clubs.events.repository.event import ClubEventRepository
from src.backend.clubs.events.schemas import CreateClubEvent, UpdateClubEvent
from src.backend.identity.auth.models import User


class ClubEventManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.event_repo = ClubEventRepository(session)

    async def create_event(
            self,
            user: User,
            club: Club,
            request: CreateClubEvent
    ) -> ClubEvent:
        is_owner_or_moderator(club, user.id)

        if request.start_at <= datetime.now(timezone.utc) or request.end_at <= datetime.now(timezone.utc):
            raise EventDateInPastError("Event start and end time can not be in past")

        if request.start_at >= request.end_at:
            raise EventDateInPastError("Event start can not be before end time")

        response = await self.event_repo.create_event(
            club_id=club.id,
            created_by_id=user.id,
            title=request.title,
            description=request.description,
            start_at=request.start_at,
            end_at=request.end_at,
            timezone=request.timezone,
            location_text=request.location_text,
            meeting_url=request.meeting_url,
        )

        await self.session.commit()
        return response

    async def update_event(
            self,
            user: User,
            club: Club,
            event: ClubEvent,
            request: UpdateClubEvent
    ) -> None:
        is_owner_or_moderator(club, user.id)

        if request.start_at:
            if request.start_at <= datetime.now(timezone.utc):
                raise EventDateInPastError("Event start time can not be in past")

        if request.end_at:
            if request.end_at <= datetime.now(timezone.utc):
                raise EventDateInPastError("Event end time can not be in past")

        response = await self.event_repo.update_event(
            event=event,
            title=request.title,
            description=request.description,
            start_at=request.start_at,
            end_at=request.end_at,
            timezone=request.timezone,
            location_text=request.location_text,
            meeting_url=request.meeting_url,
        )

        await self.session.commit()

    async def delete_event(
            self,
            user: User,
            club: Club,
            event: ClubEvent,
    ) -> None:
        is_owner_or_moderator(club, user.id)

        await self.event_repo.delete_event(
            event=event,
        )
        await self.session.commit()

    async def get_club_events(
            self,
            user: User,
            club: Club
    ) -> list[ClubEvent]:
        await is_club_member(club, user, self.session)
        events = await self.event_repo.get_club_events(
            club_id=club.id,
        )
        return events

    async def get_club_future_events(
            self,
            user: User,
            club: Club
    ) -> list[ClubEvent]:
        await is_club_member(club, user, self.session)
        events = await self.event_repo.get_club_future_events(
            club_id=club.id,
        )
        return events

    async def get_event_by_id(
            self,
            event_id: int,
    ) -> ClubEvent:
        event = await self.event_repo.get_event_by_id(
            event_id=event_id,
        )
        if not event:
            raise EventNotFoundError("Event not found")
        return event