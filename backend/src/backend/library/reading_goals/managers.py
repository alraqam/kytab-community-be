from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.library.reading_goals.dependencies import is_goal_owner
from src.backend.library.reading_goals.exceptions import ReadingGoalAlreadyExistsError, ReadingGoalNotFoundError
from src.backend.library.reading_goals.models import ReadingGoal
from src.backend.library.reading_goals.repository import ReadingGoalRepository
from src.backend.library.reading_goals.schemas import CreateReadingGoal, UpdateReadingGoal


class ReadingGoalManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.goal_repo = ReadingGoalRepository(session)

    async def create_goal(
            self,
            user: User,
            request: CreateReadingGoal
    ) -> ReadingGoal:
        try:
            response = await self.goal_repo.create_goal(
                user_id=user.id,
                year=request.year,
                target_count=request.target_count,
            )
            await self.session.commit()
            return response
        except IntegrityError:
            raise ReadingGoalAlreadyExistsError("Reading goal for this year already exists")


    async def update_goal(
            self,
            user: User,
            goal: ReadingGoal,
            request: UpdateReadingGoal
    ) -> None:
        await is_goal_owner(user, goal)

        await self.goal_repo.update_goal(
            goal=goal,
            target_count=request.target_count,
        )
        await self.session.commit()

    async def delete_goal(
            self,
            user: User,
            goal: ReadingGoal,
    ) -> None:
        await is_goal_owner(user, goal)

        await self.goal_repo.delete_goal(
            goal=goal,
        )
        await self.session.commit()

    async def get_user_goals(
            self,
            user: User,
    ) -> list[ReadingGoal]:
        result = await self.goal_repo.get_user_goals(user_id=user.id)
        return result

    async def get_goal_by_id(
            self,
            goal_id: int,
    ) -> ReadingGoal:
        result = await self.goal_repo.get_goal_by_id(goal_id=goal_id)
        if not result:
            raise ReadingGoalNotFoundError("Reading goal not found")
        return result

