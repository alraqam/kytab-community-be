from src.backend.core.exceptions import BadRequest, NotFound, Forbidden


class InvalidAvatarUrlError(BadRequest):
    """Raised when a provided avatar URL is not a valid HTTP/HTTPS URL."""

class ProfileNotFoundError(NotFound):
    """Raised when the requested profile does not exist."""

class PrivateProfileError(Forbidden):
    """Raised when attempting to view a profile whose visibility is set to private."""

class InvalidLinkUrlError(BadRequest):
    """Raised when a provided link URL is not a valid HTTP/HTTPS URL."""