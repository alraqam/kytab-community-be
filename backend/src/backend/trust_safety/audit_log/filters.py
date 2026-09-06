from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.trust_safety.audit_log.models import AuditLog
from src.backend.trust_safety.audit_log.schemas import AuditLogAction


class AuditLogFilter(Filter):
    """Query filter for audit log entries: actor, action, target object, and ordering."""

    actor_id: int | None = None
    action: AuditLogAction | None = None
    object_type: str | None = None
    object_id: int | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = AuditLog
