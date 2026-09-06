from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.trust_safety.audit_log.filters import AuditLogFilter
from src.backend.trust_safety.audit_log.models import AuditLog
from src.backend.trust_safety.audit_log.repository import AuditLogRepository


class AuditLogManager:
    """Records and retrieves immutable audit log entries for moderation and administrative actions."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.audit_log_repo = AuditLogRepository(session)

    async def log(
            self,
            actor: User,
            action: str,
            object_type: str,
            object_id: int,
            details: str | None = None,
    ) -> AuditLog:
        """Records a moderation or administrative action.

        Args:
            actor: User who performed the action.
            action: Identifier of the action taken.
            object_type: Type of the entity the action was taken on.
            object_id: ID of the entity the action was taken on.
            details: Optional free-text context.

        Returns:
            Newly created AuditLog instance.
        """
        result = await self.audit_log_repo.create_entry(
            actor_id=actor.id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            details=details,
        )
        await self.session.commit()
        return result

    async def get_logs(
            self,
            filters: AuditLogFilter
    ) -> list[AuditLog]:
        """Lists audit log entries matching the given filters.

        Args:
            filters: AuditLogFilter with actor, action, and target criteria.

        Returns:
            List of matching AuditLog instances.
        """
        return await self.audit_log_repo.get_logs(filters)
