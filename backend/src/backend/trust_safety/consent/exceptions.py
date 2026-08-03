from src.backend.core.exceptions import NotFound, BadRequest, Conflict

class DocumentNotFoundError(NotFound):
    """Raised when the requested legal document does not exist."""

class OutdatedDocumentError(Conflict):
    """Raised when a user tries to consent to a legal document version that is no longer current."""

class DocumentAlreadyConsentedError(Conflict):
    """Raised when a user has already consented to the given document."""

class ConsentNotFoundError(NotFound):
    """Raised when the requested consent record does not exist."""
