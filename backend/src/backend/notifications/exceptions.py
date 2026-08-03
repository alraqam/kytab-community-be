from src.backend.core.exceptions import NotFound, Forbidden, Conflict


class NotificationNotFoundError(NotFound):
    """Raised when the requested notification does not exist."""

class IsNotNotificationOwnerError(Forbidden):
    """Raised when a user tries to access or change a notification they don't own."""

class NotificationPreferenceNotFoundError(NotFound):
    """Raised when the requested notification preference does not exist."""

class IsNotNotificationPreferenceOwnerError(Forbidden):
    """Raised when a user tries to access or change a notification preference they don't own."""

class NotificationPreferenceAlreadyExistsError(Conflict):
    """Raised when a preference for the given category and club already exists for the user."""
