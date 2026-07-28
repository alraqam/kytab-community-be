from src.backend.core.exceptions import Conflict, NotFound


class DateInPastError(Conflict):
    """Raised when a provided deadline or closing date is in the past."""


class ActiveSessionError(Conflict):
    """Raised when an operation requires an active session but the session is not active, or vice versa."""


class ReadingSessionNotFound(NotFound):
    """Raised when a reading session with the given ID does not exist."""

class ActiveSessionNotFoundError(NotFound):
    """Raised when no active reading session exists for the club."""

class MaxActiveSessionsError(Conflict):
    pass

class MilestoneAlreadyExistsError(Conflict):
    pass

class MilestoneNotFoundError(NotFound):
    pass