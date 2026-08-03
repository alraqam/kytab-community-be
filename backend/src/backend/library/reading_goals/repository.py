from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.reading_goals.models import ReadingGoal


@dataclass
class ReadingGoalRepository:
    """Data-access layer for reading goal persistence and queries."""

    session: AsyncSession

    async def create_goal(
            self,
            user_id: int,
            year: int,
            target_count: int,
    ) -> ReadingGoal:
        """Inserts a new reading goal for a user in a given year.

        Args:
            user_id: ID of the user the goal belongs to.
            year: Year the goal targets.
            target_count: Number of books targeted for the year.

        Returns:
            Newly created ReadingGoal instance.
        """
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
        """Updates a reading goal's target count.

        Args:
            goal: ReadingGoal instance to update.
            target_count: New target count to set.
        """
        goal.target_count = target_count
        self.session.add(goal)
        await self.session.flush()

    async def delete_goal(
            self,
            goal: ReadingGoal,
    ) -> None:
        """Deletes a reading goal.

        Args:
            goal: ReadingGoal instance to delete.
        """
        await self.session.delete(goal)
        await self.session.flush()

    async def get_user_goals(
            self,
            user_id: int
    ) -> list[ReadingGoal]:
        """Lists all reading goals belonging to a user.

        Args:
            user_id: ID of the user whose goals to fetch.

        Returns:
            List of matching ReadingGoal instances.
        """
        stmt = select(ReadingGoal).where(ReadingGoal.user_id == user_id)
        result = await self.session.execute(stmt)
        goals = result.scalars().all()
        return goals

    async def get_goal_by_id(
            self,
            goal_id: int
    ) -> ReadingGoal | None:
        """Fetches a single reading goal by ID.

        Args:
            goal_id: ID of the reading goal to fetch.

        Returns:
            Matching ReadingGoal instance, or None if not found.
        """
        stmt = select(ReadingGoal).where(ReadingGoal.id == goal_id)
        result = await self.session.execute(stmt)
        goal = result.scalar_one_or_none()
        return goal