from src.backend.core.exceptions import Conflict, Forbidden, NotFound


class ProgressLogAlreadyExists(Conflict):
    """Raised when a progress log for the same user, session, and date already exists."""


class IsNotProgressLogOwnerError(Forbidden):
    """Raised when a user tries to modify a progress log they did not create."""


class ProgressLogNotFound(NotFound):
    """Raised when a progress log with the given ID does not exist."""


class SessionParticipantAlreadyExistsError(Conflict):
    """Raised when a participant record for the same user and session already exists."""


class SessionParticipantNotFoundError(NotFound):
    """Raised when a session participant record does not exist."""


class NoTotalPagesError(NotFound):
    """Raised when recommended pages cannot be calculated because the book has no page count."""

class ReadingPeriodNotFound(NotFound):
    pass