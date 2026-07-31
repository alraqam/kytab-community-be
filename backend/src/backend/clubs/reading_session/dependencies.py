from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.exceptions import IsNotProgressOwner, ProgressNotInMilestone, \
    MilestoneNotInReadingSessionError, ReadingSessionNotInClubError
from src.backend.clubs.reading_session.models import MilestoneProgress
from src.backend.identity.auth.models import User
from src.backend.clubs.reading_session.managers.milestone import MilestoneManager
from src.backend.clubs.reading_session.managers.session import ReadingSessionManager
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.core.dependencies import get_db


async def get_reading_session_manager(
        session: AsyncSession = Depends(get_db)
) -> ReadingSessionManager:
    return ReadingSessionManager(session)

async def get_reading_session_or_404(
        session_id: int,
        club: Club = Depends(get_club_or_404),
        manager: ReadingSessionManager = Depends(get_reading_session_manager)
) -> ReadingSession:
    session = await manager.get_session_by_id(session_id)
    if session.club_id != club.id:
        raise ReadingSessionNotInClubError("Reading session not found in this club")
    return session

async def get_milestone_manager(
        session: AsyncSession = Depends(get_db)
) -> MilestoneManager:
    return MilestoneManager(session)

async def get_milestone_or_404(
        milestone_id: int,
        session: ReadingSession = Depends(get_reading_session_or_404),
        manager: MilestoneManager = Depends(get_milestone_manager)
) -> Milestone:
    milestone = await manager.get_milestone_by_id(milestone_id)
    if milestone.session_id != session.id:
        raise MilestoneNotInReadingSessionError("Milestone not found in this reading session")
    return milestone

async def is_milestone_progress_owner(
        progress: MilestoneProgress,
        user: User,
):
    if progress.user_id != user.id:
        raise IsNotProgressOwner("Is not milestone progress owner")
    return True

from src.backend.clubs.reading_session.managers.progress import MilestoneProgressManager

async def get_milestone_progress_manager(
        session: AsyncSession = Depends(get_db)
) -> MilestoneProgressManager:
    return MilestoneProgressManager(session)

async def get_milestone_progress_or_404(
        progress_id: int,
        milestone: Milestone = Depends(get_milestone_or_404),
        manager: MilestoneProgressManager = Depends(get_milestone_progress_manager)
) -> MilestoneProgress:
    progress = await manager.get_milestone_by_id(progress_id)
    if progress.milestone_id != milestone.id:
        raise ProgressNotInMilestone("Progress not found in this milestone")
    return progress
