from src.backend.core.exceptions import NotFound, Forbidden, Conflict


class FollowNotFoundError(NotFound):
    """Raised when the requested follow relationship does not exist."""

class NotFollowOwnerError(Forbidden):
    """Raised when a user tries to modify a follow relationship they do not own."""

class UserAlreadyFollowingError(Conflict):
    """Raised when a user tries to follow someone they already follow."""

class NotUserFollowerError(Forbidden):
    """Raised when the checked user is not a follower of the target user."""