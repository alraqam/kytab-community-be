from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.trust_safety.audit_log.dependencies import get_audit_log_manager
from src.backend.trust_safety.audit_log.filters import AuditLogFilter
from src.backend.trust_safety.audit_log.managers import AuditLogManager
from src.backend.trust_safety.audit_log.schemas import GetAuditLog

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
        response_model=list[GetAuditLog]
    )
    async def get_logs(
            self,
            filters: AuditLogFilter = FilterDepends(AuditLogFilter)
    ):
        """Lists audit log entries, optionally filtered."""
        result = await self.manager.get_logs(filters)
        return result
