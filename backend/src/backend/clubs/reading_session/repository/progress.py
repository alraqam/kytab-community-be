from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.models import MilestoneProgress


@dataclass
class MilestoneProgressRepository:
    session: AsyncSession

    async def create_milestone_progress(
            self,
            session_id: int,
            milestone_id: int,
            user_id: int,
    ) -> MilestoneProgress:
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
        progress.milestone_id = milestone_id
        self.session.add(progress)
        await self.session.flush()

    async def update_milestone_progress_finished(
            self,
            progress: MilestoneProgress,
            status: bool
    ) -> None:
        progress.is_finished = status
        self.session.add(progress)
        await self.session.flush()

    async def delete_milestone_progress(
            self,
            progress: MilestoneProgress
    ) -> None:
        await self.session.delete(progress)
        await self.session.flush()

    async def get_user_milestone_progress(
            self,
            session_id: int,
            user_id: int
    ) -> MilestoneProgress | None:
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
        stmt = select(MilestoneProgress).where(MilestoneProgress.session_id == session_id)
        result = await self.session.execute(stmt)
        progresses = result.scalars().all()
        return progresses

    async def get_milestone_progress_by_id(
            self,
            progress_id: int
    ) -> MilestoneProgress | None:
        stmt = select(MilestoneProgress).where(MilestoneProgress.id == progress_id)
        result = await self.session.execute(stmt)
        progress = result.scalar_one_or_none()
        return progress

