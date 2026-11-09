from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.library.reading_goals.dependencies.reading_goal import get_goal_manager, get_goal_or_404
from src.backend.library.reading_goals.managers.reading_goal import ReadingGoalManager
from src.backend.library.reading_goals.models.reading_goal import ReadingGoal
from src.backend.library.reading_goals.schemas.reading_goal import GetReadingGoal, CreateReadingGoal, UpdateReadingGoal
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/reading_goal",
    tags=["reading_goal"]
)

@cbv(router)
class ReadingGoalRouter:
    """CBV router for a user's personal reading goals: create, update, delete, and retrieve."""

    goal_manager: ReadingGoalManager = Depends(get_goal_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating reading goal",
        response_model=GetReadingGoal,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 409),
    )
    async def create_goal(
            self,
            request: CreateReadingGoal
    ):
        """Creates a new reading goal for the current user."""
        result = await self.goal_manager.create_goal(self.user, request)
        return result

    @router.put(
        "/{goal_id}",
        summary="updating reading goal",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def update_goal(
            self,
            request: UpdateReadingGoal,
            goal: ReadingGoal = Depends(get_goal_or_404),
    ):
        """Updates the current user's reading goal target count."""
        await self.goal_manager.update_goal(self.user, goal, request)

    @router.delete(
        "/{goal_id}",
        summary="deleting reading goal",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_goal(
            self,
            goal: ReadingGoal = Depends(get_goal_or_404),
    ):
        """Deletes the current user's reading goal."""
        await self.goal_manager.delete_goal(self.user, goal)

    @router.get(
        "/",
        summary="getting user's reading goals",
        response_model=list[GetReadingGoal],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_user_goals(self):
        """Lists all reading goals belonging to the current user."""
        result = await self.goal_manager.get_user_goals(self.user)
        return result

    @router.get(
        "/{goal_id}",
        summary="getting reading goal by id",
        response_model=GetReadingGoal,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_goal_by_id(
            self,
            goal_id: int
    ):
        """Fetches a single reading goal by ID."""
        result = await self.goal_manager.get_goal_by_id(goal_id)
        return result