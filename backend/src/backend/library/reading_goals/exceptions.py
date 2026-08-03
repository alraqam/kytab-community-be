from src.backend.core.exceptions import Conflict, Forbidden, NotFound


class ReadingGoalAlreadyExistsError(Conflict):
    """Raised when a reading goal for the given user and year already exists."""

class IsNotGoalOwnerError(Forbidden):
    """Raised when a user attempts to act on a reading goal they do not own."""

class ReadingGoalNotFoundError(NotFound):
    """Raised when the requested reading goal does not exist."""