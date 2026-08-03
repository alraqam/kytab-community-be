from src.backend.core.exceptions import Forbidden, BadRequest, NotFound, Conflict


class IsNotShelfOwnerError(Forbidden):
    """Raised when a user who is not the shelf's owner attempts to modify or access it."""

class ShelfAlreadyExistsError(Conflict):
    """Raised when the user already has a shelf with the given name."""

class DefaultShelfError(BadRequest):
    """Raised when an attempt is made to rename or delete a default shelf."""

class ShelfNotFoundError(NotFound):
    """Raised when the requested shelf does not exist."""

class PrivateShelfError(Forbidden):
    """Raised when a shelf's visibility does not permit the requesting user to view it."""

class ShelfItemNotFoundError(NotFound):
    """Raised when the requested shelf item does not exist."""

class WorkAlreadyInShelfError(Conflict):
    """Raised when the work is already present in the user's shelf."""

class ShelfItemNotInShelfError(NotFound):
    """Raised when the shelf item does not belong to the specified shelf."""