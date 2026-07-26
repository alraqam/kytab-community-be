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
    pass

class GenreWorkLinkExistsError(Conflict):
    pass

class SeriesWorkLinkExistsError(Conflict):
    pass

class InvalidWorkEditionError(Conflict):
    pass