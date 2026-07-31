from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.events.dependencies import get_club_event_or_404, get_event_rsvp_manager
from src.backend.clubs.events.filters import EventRSVPFilter
from src.backend.clubs.events.managers.rsvp import EventRSVPManager
from src.backend.clubs.events.models import ClubEvent
from src.backend.clubs.events.schemas import GetEventRSVP, CreateEventRSVP
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{event_id}/rsvp",
    tags=["events"]
)


@cbv(router)
class EventRSVPRouter:
    event_manager: EventRSVPManager = Depends(get_event_rsvp_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    event: ClubEvent = Depends(get_club_event_or_404)

    @router.post(
        "/",
        summary="creating rsvp",
        response_model=GetEventRSVP
    )
    async def create_event(
            self,
            request: CreateEventRSVP
    ):
        result = await self.event_manager.create_rsvp(self.user, self.club, self.event, request)
        return result

    @router.get(
        "/",
        summary="getting event rsvp",
        response_model=list[GetEventRSVP]
    )
    async def get_event_rsvps(
            self,
            filters: EventRSVPFilter = FilterDepends(EventRSVPFilter),
    ):
        result = await self.event_manager.get_event_rsvps(self.user, self.club, self.event, filters)
        return result

    @router.get(
        "/results",
        summary="getting event rsvp results",
        response_model=dict
    )
    async def get_event_rsvp_results(self):
        result = await self.event_manager.get_event_rsvp_results(self.user, self.club, self.event)
        return result
