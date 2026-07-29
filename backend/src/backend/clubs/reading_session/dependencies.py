from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.exceptions import IsNotProgressOwner
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
        manager: ReadingSessionManager = Depends(get_reading_session_manager)
) -> ReadingSession:
    result = await manager.get_session_by_id(session_id)
    return result

async def get_milestone_manager(
        session: AsyncSession = Depends(get_db)
) -> MilestoneManager:
    return MilestoneManager(session)

async def get_milestone_or_404(
        milestone_id: int,
        manager: MilestoneManager = Depends(get_milestone_manager)
) -> Milestone:
    result = await manager.get_milestone_by_id(milestone_id)
    return result

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
        manager: MilestoneProgressManager = Depends(get_milestone_progress_manager)
) -> MilestoneProgress:
    result = await manager.get_milestone_by_id(progress_id)
    return result
