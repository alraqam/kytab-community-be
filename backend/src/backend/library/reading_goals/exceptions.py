from src.backend.core.exceptions import Conflict, Forbidden, NotFound


class ReadingGoalAlreadyExistsError(Conflict):
    pass

class IsNotGoalOwnerError(Forbidden):
    pass

class ReadingGoalNotFoundError(NotFound):
    pass