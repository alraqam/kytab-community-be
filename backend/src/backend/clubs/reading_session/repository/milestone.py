from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.filters import MilestoneFilter
from src.backend.clubs.reading_session.models import Milestone


@dataclass
class MilestoneRepository:
    """Data-access layer for milestone persistence and queries."""

    session: AsyncSession

    async def create_milestone(
            self,
            session_id: int,
            label: str,
            boundary_type: str,
            boundary_value: int,
            target_date: date,
            order_index: int,
    ) -> Milestone:
        """Inserts a new milestone.

        Args:
            session_id: ID of the reading session the milestone belongs to.
            label: Display label for the milestone.
            boundary_type: Type of boundary (page, chapter, or percent).
            boundary_value: Boundary value corresponding to the boundary type.
            target_date: Date the milestone is targeted for.
            order_index: Position of the milestone within the session's schedule.

        Returns:
            Newly created Milestone instance.
        """
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
            label: str | None = None,
            boundary_type: str | None = None,
            boundary_value: int | None = None,
            target_date: date | None = None,
            order_index: int | None = None,
    ) -> None:
        """Updates the given fields of a milestone, skipping unset ones.

        Args:
            milestone: Milestone instance to update.
            label: New label, or None to leave unchanged.
            boundary_type: New boundary type, or None to leave unchanged.
            boundary_value: New boundary value, or None to leave unchanged.
            target_date: New target date, or None to leave unchanged.
            order_index: New order index, or None to leave unchanged.
        """
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
        """Deletes a milestone.

        Args:
            milestone: Milestone instance to delete.
        """
        await self.session.delete(milestone)
        await self.session.flush()

    async def exists_milestone(
            self,
            session_id: int,
            boundary_type: str,
            boundary_value: int,
    ) -> list[Milestone]:
        """Finds milestones in a session matching the given boundary type and value.

        Args:
            session_id: ID of the reading session to search within.
            boundary_type: Boundary type to match.
            boundary_value: Boundary value to match.

        Returns:
            List of matching Milestone instances.
        """
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
        """Lists a reading session's milestones, optionally filtered and sorted.

        Args:
            session_id: ID of the reading session.
            filters: MilestoneFilter to apply, or None for no filtering.

        Returns:
            List of matching Milestone instances.
        """
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
        """Fetches a single milestone by ID.

        Args:
            milestone_id: ID of the milestone to fetch.

        Returns:
            Matching Milestone instance, or None if not found.
        """
        stmt = select(Milestone).where(Milestone.id == milestone_id)
        result = await self.session.execute(stmt)
        milestone = result.scalar_one_or_none()
        return milestone

