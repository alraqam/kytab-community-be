from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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