from src.backend.core.exceptions import NotFound, Forbidden, Conflict


class FollowNotFoundError(NotFound):
    pass

class NotFollowOwnerError(Forbidden):
    pass

class UserAlreadyFollowingError(Conflict):
    pass

class NotUserFollowerError(Forbidden):
    pass