from src.backend.core.exceptions import NotFound, BadRequest


class ComplaintNotFoundError(NotFound):
    pass

class ComplaintStatusError(BadRequest):
    pass

class InvalidComplaintActionError(BadRequest):
    pass