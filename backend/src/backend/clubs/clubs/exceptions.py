from src.backend.core.exceptions import NotFound, Forbidden, Conflict, BadRequest


class ClubNotFoundError(NotFound):
    """Raised when the requested club does not exist."""

class InvalidCoverUrlError(BadRequest):
    """Raised when a club cover URL is not a valid URL format."""

class IsNotClubOwnerError(Forbidden):
    """Raised when the user is not the owner of the club."""