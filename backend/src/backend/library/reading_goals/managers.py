from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.library.reading_goals.dependencies import is_goal_owner
from src.backend.library.reading_goals.exceptions import ReadingGoalAlreadyExistsError, ReadingGoalNotFoundError
from src.backend.library.reading_goals.models import ReadingGoal
from src.backend.library.reading_goals.repository import ReadingGoalRepository
from src.backend.library.reading_goals.schemas import CreateReadingGoal, UpdateReadingGoal


class ReadingGoalManager:
    """Handles reading goal business logic: creation, updates, and retrieval."""

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
        """Creates a new reading goal for a user.

        Args:
            user: User creating the reading goal.
            request: CreateReadingGoal payload with year and target count.

        Returns:
            Newly created ReadingGoal instance.

        Raises:
            ReadingGoalAlreadyExistsError: When a reading goal for that year already exists.
        """
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
        """Updates a reading goal's target count after verifying ownership.

        Args:
            user: User requesting the update.
            goal: ReadingGoal instance to update.
            request: UpdateReadingGoal payload with the new target count.

        Raises:
            IsNotGoalOwnerError: When the user does not own the goal.
        """
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
        """Deletes a reading goal after verifying ownership.

        Args:
            user: User requesting the deletion.
            goal: ReadingGoal instance to delete.

        Raises:
            IsNotGoalOwnerError: When the user does not own the goal.
        """
        await is_goal_owner(user, goal)

        await self.goal_repo.delete_goal(
            goal=goal,
        )
        await self.session.commit()

    async def get_user_goals(
            self,
            user: User,
    ) -> list[ReadingGoal]:
        """Lists all reading goals belonging to a user.

        Args:
            user: User whose reading goals to fetch.

        Returns:
            List of matching ReadingGoal instances.
        """
        result = await self.goal_repo.get_user_goals(user_id=user.id)
        return result

    async def get_goal_by_id(
            self,
            goal_id: int,
    ) -> ReadingGoal:
        """Fetches a single reading goal by ID.

        Args:
            goal_id: ID of the reading goal to fetch.

        Returns:
            Matching ReadingGoal instance.

        Raises:
            ReadingGoalNotFoundError: When no reading goal matches the ID.
        """
        result = await self.goal_repo.get_goal_by_id(goal_id=goal_id)
        if not result:
            raise ReadingGoalNotFoundError("Reading goal not found")
        return result

