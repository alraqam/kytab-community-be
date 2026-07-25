from src.backend.core.exceptions import BadRequest, Forbidden, NotFound


class InvalidRatingError(BadRequest):
    """Raised when a provided review rating is outside the allowed range."""


class IsNotReviewOwnerError(Forbidden):
    """Raised when a user tries to modify a review they did not create."""


class ReviewNotFound(NotFound):
    """Raised when a review with the given ID does not exist."""