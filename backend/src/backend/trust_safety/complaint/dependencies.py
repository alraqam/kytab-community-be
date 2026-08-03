from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.complaint.managers import ComplaintManager
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.core.dependencies import get_db


async def get_complaint_manager(
        session: AsyncSession = Depends(get_db)
) -> ComplaintManager:
    """Builds a ComplaintManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        ComplaintManager instance.
    """
    return ComplaintManager(session)

async def get_complaint_or_404(
        complaint_id: int,
        manager: ComplaintManager = Depends(get_complaint_manager)
) -> Complaint:
    """Resolves a complaint by path parameter or raises if it doesn't exist.

    Args:
        complaint_id: ID of the complaint from the path.
        manager: ComplaintManager used to look up the complaint.

    Returns:
        Complaint instance.

    Raises:
        ComplaintNotFoundError: When no complaint matches the ID.
    """
    return await manager.get_complaint_by_id(complaint_id)