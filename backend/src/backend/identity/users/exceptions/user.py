from src.backend.core.exceptions import Forbidden, BadRequest, NotFound


class PermissionDeniedError(Forbidden):
    """Raised when a user lacks the platform role (admin or platform moderator) required for an operation."""


class UserNotFoundError(NotFound):
    """Raised when a user with the given ID does not exist."""


class InvalidUserRoleError(BadRequest):
    """Raised when an invalid role value is provided for a user."""

class UserDeletionError(BadRequest):
    """Raised when a error occurs while attempting to delete a user."""