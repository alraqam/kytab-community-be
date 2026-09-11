from functools import wraps
from typing import Callable

from src.backend.trust_safety.audit_log.managers import AuditLogManager
from src.backend.trust_safety.audit_log.schemas import AuditLogAction


def audit_action(
        action: AuditLogAction,
        object_type: str,
        id_from: str = "result",
        details_from: Callable[..., str | None] | None = None,
):
    """Decorator for moderation/admin CBV route methods that records an audit log entry once the action succeeds.

    Attaching this to a route is the whole audit-logging step: unlike a manual
    `audit_log_manager.log(...)` call buried inside a manager, it lives next to the
    route's permission gate (e.g. `is_admin`), so a new moderation or admin action
    can't ship unaudited by omission. The wrapped method's own manager
    (`self.manager`) supplies the database session, and `self.user` (the CBV
    router's authenticated actor) is recorded as the actor.

    Args:
        action: Action identifier to record.
        object_type: Type of the entity the action was taken on.
        id_from: Name of the route method's keyword argument holding the target
            entity (its `.id` is used as the object ID), or "result" to use the
            `.id` of the method's return value, for actions that create a new entity.
        details_from: Optional callable receiving the route method's keyword
            arguments and returning the free-text `details` to record, or None.

    Returns:
        A decorator to apply to a router's async CBV method.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            target = result if id_from == "result" else kwargs[id_from]
            await AuditLogManager(self.manager.session).log(
                actor=self.user,
                action=action,
                object_type=object_type,
                object_id=target.id,
                details=details_from(**kwargs) if details_from else None,
            )
            return result
        return wrapper
    return decorator
