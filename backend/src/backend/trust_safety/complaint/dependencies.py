from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.complaint.managers import ComplaintManager
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.core.dependencies import get_db


async def get_complaint_manager(
        session: AsyncSession = Depends(get_db)
) -> ComplaintManager:
    return ComplaintManager(session)

async def get_complaint_or_404(
        complaint_id: int,
        manager: ComplaintManager = Depends(get_complaint_manager)
) -> Complaint:
    return await manager.get_complaint_by_id(complaint_id)