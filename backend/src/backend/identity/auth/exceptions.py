from src.backend.core.exceptions import Unauthorized, Conflict, BadRequest, Forbidden, NotFound


class InvalidTokenError(Unauthorized):
    """Raised when a JWT token is missing, expired, or has an invalid signature."""

class InvalidUsernameError(BadRequest):
    """Raised when a username does not match the required format."""

class WeakPasswordError(BadRequest):
    """Raised when a password fails strength requirements."""

class SamePasswordError(Conflict):
    """Raised when the new password is identical to the current password."""

class InvalidUsernameOrPasswordError(Conflict):
    """Raised when login credentials do not match any user."""

class UsernameAlreadyExists(Conflict):
    """Raised when a registration or update attempts to use an already taken username."""

class EmailAlreadyExists(Conflict):
    """Raised when a registration or update attempts to use an already registered email."""

class LinkExpiredError(BadRequest):
    pass

class InvalidTokenTypeError(BadRequest):
    pass

class UnverifiedUserError(Forbidden):
    pass

class NotSessionOwnerError(Forbidden):
    pass

class SessionNotFoundError(NotFound):
    pass

class UserDeletionError(BadRequest):
    pass