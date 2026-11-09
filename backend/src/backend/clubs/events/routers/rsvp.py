from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.events.dependencies.event import get_club_event_or_404, get_event_rsvp_manager
from src.backend.clubs.events.filters.event import EventRSVPFilter
from src.backend.clubs.events.managers.rsvp import EventRSVPManager
from src.backend.clubs.events.models.event import ClubEvent
from src.backend.clubs.events.schemas.event import GetEventRSVP, CreateEventRSVP
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{event_id}/rsvp",
    tags=["events"]
)


@cbv(router)
class EventRSVPRouter:
    """CBV router for RSVPs to a club event: create, list, and view results."""

    event_manager: EventRSVPManager = Depends(get_event_rsvp_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    event: ClubEvent = Depends(get_club_event_or_404)

    @router.post(
        "/",
        summary="creating rsvp",
        response_model=GetEventRSVP,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404, 409),
    )
    async def create_event(
            self,
            request: CreateEventRSVP
    ):
        """Creates an RSVP for the current user on the event."""
        result = await self.event_manager.create_rsvp(self.user, self.club, self.event, request)
        return result

    @router.get(
        "/",
        summary="getting event rsvp",
        response_model=list[GetEventRSVP],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_event_rsvps(
            self,
            filters: EventRSVPFilter = FilterDepends(EventRSVPFilter),
    ):
        """Lists RSVPs for the event, optionally filtered and sorted."""
        result = await self.event_manager.get_event_rsvps(self.user, self.club, self.event, filters)
        return result

    @router.get(
        "/results",
        summary="getting event rsvp results",
        response_model=dict,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_event_rsvp_results(self):
        """Tallies RSVP responses for the event by status."""
        result = await self.event_manager.get_event_rsvp_results(self.user, self.club, self.event)
        return result
