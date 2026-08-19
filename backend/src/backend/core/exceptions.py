
class Unauthorized(Exception):
    """Raised when a request lacks valid authentication credentials."""


class Forbidden(Exception):
    """Raised when an authenticated user lacks permission for the requested action."""


class NotFound(Exception):
    """Raised when a requested resource does not exist."""


class Conflict(Exception):
    """Raised when a request conflicts with existing data (e.g. duplicate entry)."""


class BadRequest(Exception):
    """Raised when the request contains invalid or malformed data."""


class ServiceUnavailable(Exception):
    """Raised when an upstream/external service cannot be reached or times out."""


class TooManyRequests(Exception):
    """Raised when a client is rate-limited or locked out after repeated failures."""