from src.backend.core.exceptions import NotFound, Forbidden, Conflict


class BlockNotFoundError(NotFound):
    pass

class NotBlockOwnerError(Forbidden):
    pass

class UserAlreadyBlockedError(Conflict):
    pass

class BlockedUserError(Forbidden):
    pass