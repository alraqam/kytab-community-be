from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reading_goals.models import ReadingGoal


@dataclass
class ReadingGoalRepository:
    session: AsyncSession

    async def create_goal(
            self,
            user_id: int,
            year: int,
            target_count: int,
    ) -> ReadingGoal:
        result = ReadingGoal(
            user_id=user_id,
            year=year,
            target_count=target_count,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_goal(
            self,
            goal: ReadingGoal,
            target_count: int,
    ) -> None:
        goal.target_count = target_count
        self.session.add(goal)
        await self.session.flush()

    async def delete_goal(
            self,
            goal: ReadingGoal,
    ) -> None:
        await self.session.delete(goal)
        await self.session.flush()

    async def get_user_goals(
            self,
            user_id: int
    ) -> list[ReadingGoal]:
        stmt = select(ReadingGoal).where(ReadingGoal.user_id == user_id)
        result = await self.session.execute(stmt)
        goals = result.scalars().all()
        return goals

    async def get_goal_by_id(
            self,
            goal_id: int
    ) -> ReadingGoal | None:
        stmt = select(ReadingGoal).where(ReadingGoal.id == goal_id)
        result = await self.session.execute(stmt)
        goal = result.scalar_one_or_none()
        return goal