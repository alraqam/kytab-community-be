from src.backend.core.exceptions import NotFound, Conflict


class LibrarianSubmissionNotFoundError(NotFound):
    """Raised when the requested librarian submission does not exist."""

class LibrarySubmissionStatusError(Conflict):
    """Raised when a submission's current status does not allow the requested transition."""