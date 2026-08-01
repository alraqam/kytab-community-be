from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.complaint.filters import ComplaintFilter
from src.backend.trust_safety.complaint.models import Complaint


@dataclass
class ComplaintRepository:
    session: AsyncSession

    async def create_complaint(
            self,
            reporter_id: int,
            object_type: str,
            object_id: int,
            category: str,
            comment: str,
    ) -> Complaint:
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
        complaint.status = status
        self.session.add(complaint)
        await self.session.flush()

    async def resolve_complaint(
            self,
            user_id: int,
            complaint: Complaint,
    ) -> None:
        complaint.resolved_by_id = user_id
        complaint.resolved_at = datetime.now()
        self.session.add(complaint)
        await self.session.flush()

    async def get_complaints(
            self,
            filters: ComplaintFilter
    ) -> list[Complaint]:
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
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        result = await self.session.execute(stmt)
        complaint = result.scalar_one_or_none()
        return complaint

