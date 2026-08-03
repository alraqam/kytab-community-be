from src.backend.core.exceptions import NotFound


class AnnouncementNotFoundError(NotFound):
    """Raised when the requested announcement does not exist."""
