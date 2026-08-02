from datetime import datetime, timezone, date

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_member
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.events.exceptions import EventDateInPastError, EventNotFoundError
from src.backend.clubs.events.models import ClubEvent
from src.backend.clubs.events.repository.event import ClubEventRepository
from src.backend.clubs.events.schemas import CreateClubEvent, UpdateClubEvent
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType


class ClubEventManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.event_repo = ClubEventRepository(session)
        self.membership_manager = ClubMembershipManager(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)

    async def _notify_other_members(
            self,
            user: User,
            club: Club,
            category: str,
            title: str,
            object_type: str,
            object_id: int,
    ) -> None:
        memberships = await self.membership_manager.get_memberships(club, user)
        recipients = [
            await self.user_manager.get_user_by_id(membership.user_id)
            for membership in memberships
            if membership.user_id != user.id
        ]
        await self.notification_manager.notify_many(
            recipients,
            category=category,
            title=title,
            object_type=object_type,
            object_id=object_id,
            club_id=club.id,
        )

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

        await self._notify_other_members(
            user, club,
            category=NotificationCategory.general,
            title=f"New event in {club.name}: {response.title}",
            object_type=NotificationObjectType.event,
            object_id=response.id,
        )
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

        await self._notify_other_members(
            user, club,
            category=NotificationCategory.general,
            title=f"Event updated in {club.name}: {event.title}",
            object_type=NotificationObjectType.event,
            object_id=event.id,
        )

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

    async def get_event_with_date(
            self,
            start_date: date
    ):
        events = await self.event_repo.get_event_with_time(
            start_date=start_date,
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