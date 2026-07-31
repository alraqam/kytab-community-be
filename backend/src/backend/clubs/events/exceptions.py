from src.backend.core.exceptions import Conflict, NotFound


class EventDateInPastError(Conflict):
    pass

class EventNotFoundError(NotFound):
    pass

class EventNotInClubError(NotFound):
    pass

class RsvpNotFoundError(NotFound):
    pass