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
    """Verifies that the given user owns the reading goal.

    Args:
        user: User to check ownership for.
        goal: ReadingGoal instance to check.

    Raises:
        IsNotGoalOwnerError: When the user does not own the goal.
    """
    if goal.user_id != user.id:
        raise IsNotGoalOwnerError("Only reading goal owner can change their goal")
    return

from src.backend.library.reading_goals.managers import ReadingGoalManager

async def get_goal_manager(
        session: AsyncSession = Depends(get_db)
) -> ReadingGoalManager:
    """Builds a ReadingGoalManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        ReadingGoalManager instance.
    """
    return ReadingGoalManager(session)

async def get_goal_or_404(
        goal_id: int,
        manager: ReadingGoalManager = Depends(get_goal_manager)
) -> ReadingGoal:
    """Resolves a reading goal by path parameter or raises if it doesn't exist.

    Args:
        goal_id: ID of the reading goal from the path.
        manager: ReadingGoalManager used to look up the goal.

    Returns:
        ReadingGoal instance.

    Raises:
        ReadingGoalNotFoundError: When no reading goal matches the ID.
    """
    return await manager.get_goal_by_id(goal_id)