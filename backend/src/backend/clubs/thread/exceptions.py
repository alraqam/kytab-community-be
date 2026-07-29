from src.backend.core.exceptions import Conflict, NotFound


class LockedThreadError(Conflict):
    pass

class PinnedThreadError(Conflict):
    pass

class ThreadNotFoundError(NotFound):
    pass