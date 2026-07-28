from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.filters import MilestoneFilter
from src.backend.clubs.reading_session.models import Milestone


@dataclass
class MilestoneRepository:
    session: AsyncSession

    async def create_milestone(
            self,
            session_id: int,
            label: str,
            boundary_type: str,
            boundary_value: str,
            target_date: date,
            order_index: int,
    ) -> Milestone:
        result = Milestone(
            session_id=session_id,
            label=label,
            boundary_type=boundary_type,
            boundary_value=boundary_value,
            target_date=target_date,
            order_index=order_index,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_milestone(
            self,
            milestone: Milestone,
            label: str,
            boundary_type: str,
            boundary_value: str,
            target_date: date,
            order_index: int,
    ) -> None:
        updates = {
            "label": label,
            "boundary_type": boundary_type,
            "boundary_value": boundary_value,
            "target_date": target_date,
            "order_index": order_index,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(milestone, field, value)
        await self.session.flush()

    async def delete_milestone(
            self,
            milestone: Milestone
    ) -> None:
        await self.session.delete(milestone)
        await self.session.flush()

    async def exists_milestone(
            self,
            session_id: int,
            boundary_type: str,
            boundary_value: str,
    ) -> list[Milestone]:
        stmt = (select(Milestone).where(
            and_(
                Milestone.session_id == session_id,
                Milestone.boundary_type == boundary_type,
                Milestone.boundary_value == boundary_value,
            )
        ))
        result = await self.session.execute(stmt)
        milestones = result.scalars().all()
        return milestones

    async def get_session_milestones(
            self,
            session_id: int,
            filters: MilestoneFilter  | None = None
    ) -> list[Milestone]:
        stmt = select(Milestone).where(Milestone.session_id == session_id)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        milestones = result.scalars().all()
        return milestones

    async def get_milestone_by_id(
            self,
            milestone_id: int
    ) -> Milestone | None:
        stmt = select(Milestone).where(Milestone.id == milestone_id)
        result = await self.session.execute(stmt)
        milestone = result.scalar_one_or_none()
        return milestone

