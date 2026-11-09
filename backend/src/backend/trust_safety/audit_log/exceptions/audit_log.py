from src.backend.core.exceptions import BadRequest


class AuditLogImmutableError(BadRequest):
    """Raised when code attempts to modify or delete an existing audit log entry."""
