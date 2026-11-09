from src.backend.core.exceptions import NotFound, Conflict


class BookNotFoundError(NotFound):
    """Raised when a book with the given ID does not exist."""


class WorkNotFoundError(NotFound):
    """Raised when a work with the given ID does not exist."""


class EditionNotFoundError(NotFound):
    """Raised when an edition with the given ID does not exist."""


class AuthorNotFoundError(NotFound):
    """Raised when an author with the given ID does not exist."""


class SeriesNotFoundError(NotFound):
    """Raised when a series with the given ID does not exist."""


class GenreNotFoundError(NotFound):
    """Raised when a genre with the given ID does not exist."""

class AuthorWorkLinkExistsError(Conflict):
    """Raised when an author is already linked to the given work."""

class GenreWorkLinkExistsError(Conflict):
    """Raised when a genre is already linked to the given work."""

class SeriesWorkLinkExistsError(Conflict):
    """Raised when a work is already linked to the given series."""

class InvalidWorkEditionError(Conflict):
    """Raised when an edition does not belong to the expected work."""

class DuplicateMergeError(Conflict):
    """Raised when attempting to merge a work into itself."""