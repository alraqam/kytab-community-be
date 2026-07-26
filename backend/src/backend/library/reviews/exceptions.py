from src.backend.core.exceptions import BadRequest, Forbidden, NotFound, Conflict


class InvalidRatingError(BadRequest):
    """Raised when a provided review rating is outside the allowed range."""


class IsNotReviewOwnerError(Forbidden):
    """Raised when a user tries to modify a review they did not create."""


class ReviewNotFound(NotFound):
    """Raised when a review with the given ID does not exist."""

class IsNotReviewCommentOwnerError(Forbidden):
    pass

class ReviewCommentNotFoundError(NotFound):
    pass

class IsNotReviewLikeOwnerError(Forbidden):
    pass

class ReviewLikeNotFoundError(NotFound):
    pass

class ReviewLikeAlreadyExists(Conflict):
    pass

class EmptyReviewError(BadRequest):
    pass

