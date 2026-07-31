from src.backend.core.exceptions import Forbidden, BadRequest, NotFound, Conflict


class IsNotShelfOwnerError(Forbidden):
    pass

class ShelfAlreadyExistsError(Conflict):
    pass

class DefaultShelfError(BadRequest):
    pass

class ShelfNotFoundError(NotFound):
    pass

class PrivateShelfError(Forbidden):
    pass

class ShelfItemNotFoundError(NotFound):
    pass

class WorkAlreadyInShelfError(Conflict):
    pass

class ShelfItemNotInShelfError(NotFound):
    pass