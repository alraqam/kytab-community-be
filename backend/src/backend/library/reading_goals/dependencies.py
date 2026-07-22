from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.library.reading_goals.exceptions import IsNotGoalOwnerError
from src.backend.library.reading_goals.models import ReadingGoal

from src.backend.identity.auth.models import User


async def is_goal_owner(
        user: User,
        goal: ReadingGoal,
) -> None:
    if goal.user_id != user.id:
        raise IsNotGoalOwnerError("Only reading goal owner can change their goal")
    return

from src.backend.library.reading_goals.managers import ReadingGoalManager

async def get_goal_manager(
        session: AsyncSession = Depends(get_db)
) -> ReadingGoalManager:
    return ReadingGoalManager(session)

async def get_goal_or_404(
        goal_id: int,
        manager: ReadingGoalManager = Depends(get_goal_manager)
) -> ReadingGoal:
    return await manager.get_goal_by_id(goal_id)