from src.backend.core.exceptions import NotFound, Forbidden, Conflict, BadRequest


class ClubNotFoundError(NotFound):
    """Raised when the requested club does not exist."""

class InvalidCoverUrlError(BadRequest):
    """Raised when an uploaded club cover image has an unsupported type or exceeds the size limit."""

class IsNotClubOwnerError(Forbidden):
    """Raised when the user is not the owner of the club."""