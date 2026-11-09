from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import is_admin
from src.backend.trust_safety.audit_log.dependencies.audit_log import get_audit_log_manager
from src.backend.trust_safety.audit_log.filters.audit_log import AuditLogFilter
from src.backend.trust_safety.audit_log.managers.audit_log import AuditLogManager
from src.backend.trust_safety.audit_log.schemas.audit_log import GetAuditLog
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/admin/audit-log",
    tags=["admin"]
)

@cbv(router)
class AuditLogAdminRouter:
    """CBV router for platform-level review of the immutable audit log."""

    manager: AuditLogManager = Depends(get_audit_log_manager)
    user: User = Depends(is_admin)

    @router.get(
        "/",
        summary="getting audit log entries",
        response_model=list[GetAuditLog],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403),
    )
    async def get_logs(
            self,
            filters: AuditLogFilter = FilterDepends(AuditLogFilter)
    ):
        """Lists audit log entries, optionally filtered."""
        result = await self.manager.get_logs(filters)
        return result
