from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.models import Thread, Post
from src.backend.trust_safety.complaint.filters import ComplaintFilter
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.complaint.schemas import ComplaintObjectType


@dataclass
class ComplaintRepository:
    """Data-access layer for complaint persistence and queries."""

    session: AsyncSession

    async def create_complaint(
            self,
            reporter_id: int,
            object_type: str,
            object_id: int,
            category: str,
            comment: str,
    ) -> Complaint:
        """Inserts a new pending complaint.

        Args:
            reporter_id: ID of the user filing the complaint.
            object_type: Type of entity being reported.
            object_id: ID of the entity being reported.
            category: Reason for the complaint.
            comment: Free-text details from the reporter.

        Returns:
            Newly created Complaint instance.
        """
        result = Complaint(
            reporter_id=reporter_id,
            object_type=object_type,
            object_id=object_id,
            category=category,
            comment=comment,
            resolved_by_id=None,
            resolved_at=None,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_complaint_status(
            self,
            complaint: Complaint,
            status: str
    ) -> None:
        """Sets a complaint's status.

        Args:
            complaint: Complaint instance to update.
            status: New status value.
        """
        complaint.status = status
        self.session.add(complaint)
        await self.session.flush()

    async def resolve_complaint(
            self,
            user_id: int,
            complaint: Complaint,
    ) -> None:
        """Stamps a complaint with the resolving moderator and resolution time.

        Args:
            user_id: ID of the moderator resolving the complaint.
            complaint: Complaint instance to update.
        """
        complaint.resolved_by_id = user_id
        complaint.resolved_at = datetime.now()
        self.session.add(complaint)
        await self.session.flush()

    async def update_escalated(
            self,
            complaint: Complaint,
            is_escalated: bool,
    ) -> None:
        """Sets a complaint's escalation flag.

        Args:
            complaint: Complaint instance to update.
            is_escalated: New escalation state.
        """
        complaint.is_escalated = is_escalated
        self.session.add(complaint)
        await self.session.flush()

    async def get_club_complaints(
            self,
            club_id: int,
    ) -> list[Complaint]:
        """Lists complaints filed against a club or against posts within that club.

        Args:
            club_id: ID of the club to fetch complaints for.

        Returns:
            List of matching Complaint instances.
        """
        club_post_ids = (
            select(Post.id)
            .join(Thread, Thread.id == Post.thread_id)
            .where(Thread.club_id == club_id)
        )
        stmt = select(Complaint).where(
            or_(
                and_(Complaint.object_type == ComplaintObjectType.club, Complaint.object_id == club_id),
                and_(Complaint.object_type == ComplaintObjectType.post, Complaint.object_id.in_(club_post_ids)),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_complaints(
            self,
            filters: ComplaintFilter
    ) -> list[Complaint]:
        """Lists complaints, optionally filtered and sorted.

        Args:
            filters: ComplaintFilter to apply, or None for no filtering.

        Returns:
            List of matching Complaint instances.
        """
        stmt = select(Complaint)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_complaint_by_id(
            self,
            complaint_id: int
    ) -> Complaint | None:
        """Fetches a single complaint by ID.

        Args:
            complaint_id: ID of the complaint to fetch.

        Returns:
            Matching Complaint instance, or None if not found.
        """
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        result = await self.session.execute(stmt)
        complaint = result.scalar_one_or_none()
        return complaint

