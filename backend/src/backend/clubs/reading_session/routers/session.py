from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.reading_session.dependencies import get_milestone_progress_manager
from src.backend.clubs.reading_session.managers.progress import MilestoneProgressManager
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.dependencies import get_reading_session_manager, get_reading_session_or_404
from src.backend.clubs.reading_session.managers.session import ReadingSessionManager
from src.backend.clubs.reading_session.models import ReadingSession
from src.backend.clubs.reading_session.schemas import GetReadingSession, CreateReadingSession, GetMilestoneProgress
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{club_id}/sessions",
)

@cbv(router)
class ReadingSessionRouter:
    """CBV router for club reading session endpoints."""

    manager: ReadingSessionManager = Depends(get_reading_session_manager)
    progress_manager: MilestoneProgressManager = Depends(get_milestone_progress_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.post(
        "/",
        summary="creating reading session",
        response_model=GetReadingSession,
        tags=["reading_sessions"],
    )
    async def create_session(
            self,
            request: CreateReadingSession
    ):
        """Creates a new reading session for the club."""
        result = await self.manager.create_session(self.user, self.club, request)
        return result

    @router.put(
        "/{session_id}",
        summary="completing active reading session",
        tags=["reading_sessions"],
    )
    async def complete_session(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        """Marks the specified reading session as completed."""
        await self.manager.complete_session(self.user, self.club, reading_session)

    @router.delete(
        "/{session_id}",
        summary="deleting reading session",
        tags=["reading_sessions"],
    )
    async def delete_session(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        """Deletes a non-active reading session."""
        await self.manager.delete_session(self.user, self.club, reading_session)

    @router.get(
        "/active",
        summary="getting club's active reading sessions",
        response_model=list[GetReadingSession],
        tags=["reading_sessions"],
    )
    async def get_club_active_sessions(self):
        """Returns the club's current active reading session."""
        result = await self.manager.get_club_active_sessions(self.club, self.user)
        return result

    @router.get(
        "/",
        summary="getting club's sessions",
        response_model=list[GetReadingSession],
        tags=["reading_sessions"],
    )
    async def get_club_sessions(self):
        """Returns all reading sessions for the club."""
        result = await self.manager.get_club_sessions(self.club, self.user)
        return result

    @router.get(
        "/{session_id}/progress",
        summary="getting session milestone progresses",
        response_model=list[GetMilestoneProgress],
        tags=["reading_sessions"],
    )
    async def get_session_milestone_progress(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        """Lists all milestone progress records for the reading session."""
        result = await self.progress_manager.get_session_milestone_progress(reading_session, self.user, self.club)
        return result

    @router.get(
        "/{session_id}",
        summary="getting current users milestone progress",
        response_model=GetMilestoneProgress,
        tags=["reading_sessions"],
    )
    async def get_user_milestone_progress(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        """Fetches the current user's milestone progress for the reading session."""
        result = await self.progress_manager.get_user_milestone_progress(reading_session, self.user)
        return result