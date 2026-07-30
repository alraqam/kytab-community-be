from src.backend.core.exceptions import Conflict, NotFound, Forbidden


class LockedThreadError(Conflict):
    pass

class PinnedThreadError(Conflict):
    pass

class ThreadNotFoundError(NotFound):
    pass

class IsNotPostOwnerError(Forbidden):
    pass

class PostNotFoundError(NotFound):
    pass

class IsNotPostReactionOwnerError(Forbidden):
    pass

class ReactionNotFoundError(NotFound):
    pass

class PostReactionAlreadyExists(Conflict):
    pass

class MilestoneNotReachedError(Forbidden):
    pass