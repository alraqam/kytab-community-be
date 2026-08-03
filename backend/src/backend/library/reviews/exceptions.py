from src.backend.core.exceptions import BadRequest, Forbidden, NotFound, Conflict


class InvalidRatingError(BadRequest):
    """Raised when a provided review rating is outside the allowed range."""


class IsNotReviewOwnerError(Forbidden):
    """Raised when a user tries to modify a review they did not create."""


class ReviewNotFound(NotFound):
    """Raised when a review with the given ID does not exist."""

class IsNotReviewCommentOwnerError(Forbidden):
    """Raised when a user tries to modify a review comment they did not create."""

class ReviewCommentNotFoundError(NotFound):
    """Raised when a review comment with the given ID does not exist."""

class IsNotReviewLikeOwnerError(Forbidden):
    """Raised when a user tries to modify a review like they did not create."""

class ReviewLikeNotFoundError(NotFound):
    """Raised when a review like with the given ID does not exist."""

class ReviewLikeAlreadyExists(Conflict):
    """Raised when a user tries to like a review they have already liked."""

class EmptyReviewError(BadRequest):
    """Raised when a review is created without a rating or text."""

class ReviewNotInWorkError(NotFound):
    """Raised when a review does not belong to the given work."""

class CommentNotInReviewError(NotFound):
    """Raised when a comment does not belong to the given review."""

class LikeNotInReviewError(NotFound):
    """Raised when a like does not belong to the given review."""