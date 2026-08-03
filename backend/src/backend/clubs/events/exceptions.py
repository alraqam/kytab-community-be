from src.backend.core.exceptions import Conflict, NotFound


class EventDateInPastError(Conflict):
    """Raised when an event's start or end time is invalid, such as being in the past, out of order, or already ended."""

class EventNotFoundError(NotFound):
    """Raised when the requested event does not exist."""

class EventNotInClubError(NotFound):
    """Raised when the requested event does not belong to the given club."""

class RsvpNotFoundError(NotFound):
    """Raised when the requested RSVP does not exist."""