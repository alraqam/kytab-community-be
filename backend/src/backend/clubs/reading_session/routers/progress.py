from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.reading_session.dependencies.reading_session import get_milestone_progress_manager, get_reading_session_or_404, \
     get_milestone_progress_or_404, get_milestone_or_404
from src.backend.clubs.reading_session.managers.progress import MilestoneProgressManager
from src.backend.clubs.reading_session.models.reading_session import ReadingSession, Milestone, MilestoneProgress
from src.backend.clubs.reading_session.schemas.reading_session import GetMilestoneProgress
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{milestone_id}/progress",
    tags=["milestone_progress"]
)

@cbv(router)
class MilestoneProgressRouter:
    """CBV router for managing a user's progress toward a milestone: create, update, finish, delete, and retrieve."""

    manager: MilestoneProgressManager = Depends(get_milestone_progress_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    session: ReadingSession = Depends(get_reading_session_or_404)
    milestone: Milestone = Depends(get_milestone_or_404)

    @router.post(
        "/",
        summary="creating milestone progress",
        response_model=GetMilestoneProgress,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404, 409),
    )
    async def create_milestone_progress(
            self,
    ):
        """Creates a milestone progress record for the current user."""
        result = await self.manager.create_milestone_progress(self.user, self.club, self.session, self.milestone)
        return result

    @router.put(
        "/{progress_id}",
        summary="update milestone progress",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def update_milestone_progress(
            self,
            progress: MilestoneProgress = Depends(get_milestone_progress_or_404),
    ):
        """Updates the current user's milestone progress record."""
        await self.manager.update_milestone_progress(progress, self.user, self.session, self.milestone)

    @router.put(
        "/{progress_id}/finish",
        summary="finishing milestone progress",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def finish_milestone_progress(
            self,
            progress: MilestoneProgress = Depends(get_milestone_progress_or_404),
    ):
        """Marks the current user's milestone progress as finished."""
        await self.manager.finish_milestone_progress(progress, self.user, self.session)

    @router.delete(
        "/{progress_id}",
        summary="deleting milestone progress",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_milestone_progress(
            self,
            progress: MilestoneProgress = Depends(get_milestone_progress_or_404),
    ):
        """Deletes the current user's milestone progress record."""
        await self.manager.delete_milestone_progress(progress, self.user)

    @router.get(
        "/{progress_id}",
        summary="getting milestone progress by id",
        response_model=GetMilestoneProgress,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_milestone_progress_by_id(
            self,
            progress: MilestoneProgress = Depends(get_milestone_progress_or_404),
    ):
        """Fetches a single milestone progress record by ID."""
        return progress