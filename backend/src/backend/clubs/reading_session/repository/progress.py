from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.models import MilestoneProgress


@dataclass
class MilestoneProgressRepository:
    """Data-access layer for milestone progress persistence and queries."""

    session: AsyncSession

    async def create_milestone_progress(
            self,
            session_id: int,
            milestone_id: int,
            user_id: int,
    ) -> MilestoneProgress:
        """Inserts a new milestone progress record.

        Args:
            session_id: ID of the reading session.
            milestone_id: ID of the milestone being tracked.
            user_id: ID of the user the progress record belongs to.

        Returns:
            Newly created MilestoneProgress instance.
        """
        result = MilestoneProgress(
            session_id=session_id,
            milestone_id=milestone_id,
            user_id=user_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_milestone_progress(
            self,
            progress: MilestoneProgress,
            milestone_id: int,
    ) -> None:
        """Updates the milestone a progress record points to.

        Args:
            progress: MilestoneProgress instance to update.
            milestone_id: ID of the milestone to associate with the progress record.
        """
        progress.milestone_id = milestone_id
        self.session.add(progress)
        await self.session.flush()

    async def update_milestone_progress_finished(
            self,
            progress: MilestoneProgress,
            status: bool
    ) -> None:
        """Sets a milestone progress record's finished flag.

        Args:
            progress: MilestoneProgress instance to update.
            status: True to mark finished, False to mark unfinished.
        """
        progress.is_finished = status
        self.session.add(progress)
        await self.session.flush()

    async def delete_milestone_progress(
            self,
            progress: MilestoneProgress
    ) -> None:
        """Deletes a milestone progress record.

        Args:
            progress: MilestoneProgress instance to delete.
        """
        await self.session.delete(progress)
        await self.session.flush()

    async def get_user_milestone_progress(
            self,
            session_id: int,
            user_id: int
    ) -> MilestoneProgress | None:
        """Fetches a user's milestone progress record for a reading session.

        Args:
            session_id: ID of the reading session.
            user_id: ID of the user.

        Returns:
            Matching MilestoneProgress instance, or None if not found.
        """
        stmt = select(MilestoneProgress).where(
            and_(
                MilestoneProgress.session_id == session_id,
                MilestoneProgress.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        progress = result.scalar_one_or_none()
        return progress

    async def get_session_milestone_progress(
            self,
            session_id: int
    ) -> list[MilestoneProgress]:
        """Lists all milestone progress records for a reading session.

        Args:
            session_id: ID of the reading session.

        Returns:
            List of matching MilestoneProgress instances.
        """
        stmt = select(MilestoneProgress).where(MilestoneProgress.session_id == session_id)
        result = await self.session.execute(stmt)
        progresses = result.scalars().all()
        return progresses

    async def get_milestone_progress_by_id(
            self,
            progress_id: int
    ) -> MilestoneProgress | None:
        """Fetches a single milestone progress record by ID.

        Args:
            progress_id: ID of the progress record to fetch.

        Returns:
            Matching MilestoneProgress instance, or None if not found.
        """
        stmt = select(MilestoneProgress).where(MilestoneProgress.id == progress_id)
        result = await self.session.execute(stmt)
        progress = result.scalar_one_or_none()
        return progress

