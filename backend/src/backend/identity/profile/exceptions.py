from src.backend.core.exceptions import BadRequest, NotFound, Forbidden


class InvalidAvatarUrlError(BadRequest):
    """Raised when a provided avatar URL is not a valid HTTP/HTTPS URL."""

class ProfileNotFoundError(NotFound):
    pass

class PrivateProfileError(Forbidden):
    pass

class InvalidLinkUrlError(BadRequest):
    pass