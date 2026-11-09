from src.backend.core.exceptions import Conflict, Forbidden, NotFound


class ProgressLogAlreadyExists(Conflict):
    """Raised when a progress log for the same user, session, and date already exists."""


class IsNotProgressLogOwnerError(Forbidden):
    """Raised when a user tries to modify a progress log they did not create."""


class ProgressLogNotFound(NotFound):
    """Raised when a progress log with the given ID does not exist."""



class NoTotalPagesError(NotFound):
    """Raised when recommended pages cannot be calculated because the book has no page count."""

class NoProgressLoggedError(NotFound):
    """Raised when reading pace cannot be estimated because no progress has been logged yet."""

class ReadingPeriodNotFound(NotFound):
    """Raised when a reading period with the given ID does not exist."""

class LogDateError(Conflict):
    """Raised when a progress log update is attempted for a date other than today."""

class ActiveReadingPeriodError(Conflict):
    """Raised when a reading period operation conflicts with its current active or finished state."""

class NotReadingPeriodOwner(Forbidden):
    """Raised when a user tries to modify a reading period they do not own."""

class ReadingPeriodNotInShelfItemError(NotFound):
    """Raised when a reading period does not belong to the given shelf item."""

class ProgressLogNotInReadingPeriodError(NotFound):
    """Raised when a progress log does not belong to the given reading period."""