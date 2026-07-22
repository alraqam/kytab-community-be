from src.backend.core.exceptions import Forbidden, BadRequest, NotFound


class PermissionDeniedError(Forbidden):
    """Raised when a non-admin user attempts an admin-only operation."""


class UserNotFoundError(NotFound):
    """Raised when a user with the given ID does not exist."""


class InvalidUserRoleError(BadRequest):
    """Raised when an invalid role value is provided for a user."""