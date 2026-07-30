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
    tags=["reading_sessions"]
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
        response_model=GetReadingSession
    )
    async def create_session(
            self,
            request: CreateReadingSession
    ):
        """Creates a new reading session for the club.

        Args:
            request: CreateReadingSession payload with book_id and deadline.
        """
        result = await self.manager.create_session(self.user, self.club, request)
        return result

    @router.put(
        "/{session_id}",
        summary="completing active reading session",
    )
    async def complete_session(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        """Marks the specified reading session as completed.

        Args:
            reading_session: ReadingSession instance resolved via get_reading_session_or_404.
        """
        await self.manager.complete_session(self.user, self.club, reading_session)

    @router.delete(
        "/{session_id}",
        summary="deleting reading session",
    )
    async def delete_session(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        """Deletes a non-active reading session.

        Args:
            reading_session: ReadingSession instance resolved via get_reading_session_or_404.
        """
        await self.manager.delete_session(self.user, self.club, reading_session)

    @router.get(
        "/active",
        summary="getting club's active reading sessions",
        response_model=list[GetReadingSession]
    )
    async def get_club_active_sessions(self):
        """Returns the club's current active reading session."""
        result = await self.manager.get_club_active_sessions(self.club)
        return result

    @router.get(
        "/",
        summary="getting club's sessions",
        response_model=list[GetReadingSession]
    )
    async def get_club_sessions(self):
        """Returns all reading sessions for the club."""
        result = await self.manager.get_club_sessions(self.club)
        return result

    @router.get(
        "/{session_id}/progress",
        summary="getting session milestone progresses",
        response_model=list[GetMilestoneProgress]
    )
    async def get_session_milestone_progress(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        """Returns all reading sessions for the club."""
        result = await self.progress_manager.get_session_milestone_progress(reading_session, self.user, self.club)
        return result

    @router.get(
        "/{session_id}",
        summary="getting current users milestone progress",
        response_model=GetMilestoneProgress
    )
    async def get_user_milestone_progress(
            self,
            reading_session: ReadingSession = Depends(get_reading_session_or_404)
    ):
        result = await self.progress_manager.get_user_milestone_progress(reading_session, self.user)
        return result