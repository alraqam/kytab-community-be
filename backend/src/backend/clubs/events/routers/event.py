from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.events.dependencies import get_club_event_manager, get_club_event_or_404
from src.backend.clubs.events.managers.event import ClubEventManager
from src.backend.clubs.events.models import ClubEvent
from src.backend.clubs.events.schemas import GetClubEvent, CreateClubEvent, UpdateClubEvent
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{club_id}/events",
)

@cbv(router)
class ClubEventRouter:
    """CBV router for club events: create, update, delete, and retrieve."""

    event_manager: ClubEventManager = Depends(get_club_event_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.post(
        "/",
        summary="creating event",
        response_model=GetClubEvent,
        tags=["events"],
    )
    async def create_event(
            self,
            request: CreateClubEvent
    ):
        """Creates a new club event."""
        result = await self.event_manager.create_event(self.user, self.club, request)
        return result

    @router.put(
        "/{event_id}",
        summary="updating event",
        tags=["events"],
    )
    async def update_event(
            self,
            request: UpdateClubEvent,
            event: ClubEvent = Depends(get_club_event_or_404),
    ):
        """Updates a club event's fields."""
        await self.event_manager.update_event(self.user, self.club, event, request)

    @router.delete(
        "/{event_id}",
        summary="deleting event",
        tags=["events"],
    )
    async def delete_event(
            self,
            event: ClubEvent = Depends(get_club_event_or_404),
    ):
        """Deletes a club event."""
        await self.event_manager.delete_event(self.user, self.club, event)

    @router.get(
        "/all",
        summary="getting club events",
        response_model=list[GetClubEvent],
        tags=["events"],
    )
    async def get_club_events(self):
        """Lists all events for the club."""
        result = await self.event_manager.get_club_events(self.user, self.club)
        return result

    @router.get(
        "/future",
        summary="getting club future events",
        response_model=list[GetClubEvent],
        tags=["events"],
    )
    async def get_club_future_events(self):
        """Lists the club's events that have not yet started."""
        result = await self.event_manager.get_club_future_events(self.user, self.club)
        return result

    @router.get(
        "/{event_id}",
        summary="getting event by id",
        response_model=GetClubEvent,
        tags=["events"],
    )
    async def get_event_by_id(
            self,
            event: ClubEvent = Depends(get_club_event_or_404),
    ):
        """Fetches a single club event by ID."""
        return event