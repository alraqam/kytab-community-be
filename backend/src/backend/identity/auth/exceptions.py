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
    """Raised when a verification or password-reset link has expired."""

class InvalidTokenTypeError(BadRequest):
    """Raised when a token's type claim does not match the expected type."""

class UnverifiedUserError(Forbidden):
    """Raised when an action requires a verified email but the user is unverified."""

class NotSessionOwnerError(Forbidden):
    """Raised when a user attempts to revoke a session they do not own."""

class SessionNotFoundError(NotFound):
    """Raised when no session matches the given ID or token."""

class UserDeletionError(BadRequest):
    """Raised when a user account cannot be deleted."""