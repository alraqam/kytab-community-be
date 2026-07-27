from src.backend.core.exceptions import NotFound, Forbidden, Conflict, BadRequest


class ClubNotFoundError(NotFound):
    pass

class InvalidCoverUrlError(BadRequest):
    pass

class IsNotClubOwnerError(Forbidden):
    pass