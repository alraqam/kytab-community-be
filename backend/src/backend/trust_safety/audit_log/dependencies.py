from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.trust_safety.audit_log.managers import AuditLogManager


async def get_audit_log_manager(
        session: AsyncSession = Depends(get_db)
) -> AuditLogManager:
    """Builds an AuditLogManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        AuditLogManager instance.
    """
    return AuditLogManager(session)
