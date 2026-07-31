from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.events.exceptions import EventNotInClubError
from src.backend.clubs.events.managers.event import ClubEventManager
from src.backend.clubs.events.managers.rsvp import EventRSVPManager
from src.backend.clubs.events.models import ClubEvent, EventRSVP
from src.backend.core.dependencies import get_db


async def get_club_event_manager(
        session: AsyncSession = Depends(get_db)
) -> ClubEventManager:
    return ClubEventManager(session)

async def get_club_event_or_404(
        event_id: int,
        club: Club = Depends(get_club_or_404),
        manager: ClubEventManager = Depends(get_club_event_manager),
) -> ClubEvent:
    event = await manager.get_event_by_id(event_id)
    if event.club_id != club.id:
        raise EventNotInClubError("Event not found in this club")
    return event


async def get_event_rsvp_manager(
        session: AsyncSession = Depends(get_db)
) -> EventRSVPManager:
    return EventRSVPManager(session)
