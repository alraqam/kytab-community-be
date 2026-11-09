from src.backend.core.exceptions import BadRequest, Conflict, Forbidden, NotFound


class InvalidGoodreadsFileError(BadRequest):
    """Raised when the uploaded file is not a valid Goodreads CSV export."""

class GoodreadsImportRowNotFoundError(NotFound):
    """Raised when the requested import row does not exist."""

class IsNotImportRowOwnerError(Forbidden):
    """Raised when a user who did not create the import row attempts to act on it."""

class ImportRowAlreadySubmittedError(Conflict):
    """Raised when an import row has already been submitted to the catalog queue."""
