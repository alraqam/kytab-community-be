from src.backend.core.exceptions import NotFound, BadRequest


class ComplaintNotFoundError(NotFound):
    """Raised when the requested complaint does not exist."""

class ComplaintStatusError(BadRequest):
    """Raised when an action requires a pending complaint but it has already been resolved or dismissed."""

class InvalidComplaintActionError(BadRequest):
    """Raised when a moderation action is attempted against a complaint type it doesn't support."""