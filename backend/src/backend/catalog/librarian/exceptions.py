from src.backend.core.exceptions import NotFound, Conflict


class LibrarianSubmissionNotFoundError(NotFound):
    pass

class LibrarySubmissionStatusError(Conflict):
    pass