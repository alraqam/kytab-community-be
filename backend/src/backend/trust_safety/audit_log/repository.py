from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.audit_log.filters import AuditLogFilter
from src.backend.trust_safety.audit_log.models import AuditLog


@dataclass
class AuditLogRepository:
    """Data-access layer for audit log persistence. Append-only: no update or delete methods are exposed."""

    session: AsyncSession

    async def create_entry(
            self,
            actor_id: int | None,
            action: str,
            object_type: str,
            object_id: int,
            details: str | None = None,
    ) -> AuditLog:
        """Inserts a new audit log entry.

        Args:
            actor_id: ID of the user who performed the action, or None if the system acted.
            action: Identifier of the action taken.
            object_type: Type of the entity the action was taken on.
            object_id: ID of the entity the action was taken on.
            details: Optional free-text context.

        Returns:
            Newly created AuditLog instance.
        """
        result = AuditLog(
            actor_id=actor_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            details=details,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_logs(
            self,
            filters: AuditLogFilter
    ) -> list[AuditLog]:
        """Lists audit log entries, optionally filtered and sorted.

        Args:
            filters: AuditLogFilter to apply, or None for no filtering.

        Returns:
            List of matching AuditLog instances.
        """
        stmt = select(AuditLog)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst
