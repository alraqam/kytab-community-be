from src.backend.core.exceptions import Conflict, NotFound, Forbidden


class LockedThreadError(Conflict):
    """Raised when an action cannot be performed because of a thread's lock state."""

class PinnedThreadError(Conflict):
    """Raised when attempting to pin a thread that is already pinned."""

class ThreadNotFoundError(NotFound):
    """Raised when the requested thread does not exist."""

class IsNotPostOwnerError(Forbidden):
    """Raised when a user attempts to act on a post they do not own."""

class PostNotFoundError(NotFound):
    """Raised when the requested post does not exist."""

class IsNotPostReactionOwnerError(Forbidden):
    """Raised when a user attempts to act on a reaction they do not own."""

class ReactionNotFoundError(NotFound):
    """Raised when the requested reaction does not exist."""

class PostReactionAlreadyExists(Conflict):
    """Raised when a user has already reacted to a post with the given emoji."""

class MilestoneNotReachedError(Forbidden):
    """Raised when a user attempts to access content for a milestone they have not reached."""

class ThreadNotInClubError(NotFound):
    """Raised when a thread does not belong to the given club."""

class ThreadNotInMilestoneError(NotFound):
    """Raised when a thread does not belong to the given milestone."""

class PostNotInThreadError(NotFound):
    """Raised when a post does not belong to the given thread."""

class ReactionNotInPostError(NotFound):
    """Raised when a reaction does not belong to the given post."""
