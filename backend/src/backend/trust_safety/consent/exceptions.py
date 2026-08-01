from src.backend.core.exceptions import NotFound, BadRequest, Conflict

class DocumentNotFoundError(NotFound):
    pass

class OutdatedDocumentError(Conflict):
    pass

class DocumentAlreadyConsentedError(Conflict):
    pass

class ConsentNotFoundError(NotFound):
    pass
