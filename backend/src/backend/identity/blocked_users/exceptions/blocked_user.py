from src.backend.core.exceptions import NotFound, Forbidden, Conflict


class BlockNotFoundError(NotFound):
    """Raised when the requested block does not exist."""

class NotBlockOwnerError(Forbidden):
    """Raised when a user other than the block's owner tries to delete it."""

class UserAlreadyBlockedError(Conflict):
    """Raised when a user tries to block someone they have already blocked."""

class BlockedUserError(Forbidden):
    """Raised when an action is attempted against a user who is blocked."""