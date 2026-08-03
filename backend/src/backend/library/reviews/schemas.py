from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.backend.library.reviews.exceptions import InvalidRatingError


class BaseReview(BaseModel):
    """Base payload for a review's rating, text, and spoiler flag."""

    rating: float| None = Field(ge=0.5, le=5.0)
    text: str | None = Field(max_length=5000)
    contains_spoiler: bool

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: float) -> float| None:
        """Ensures the rating, if provided, falls on a 0.5 increment.

        Args:
            value: Rating value to validate.

        Returns:
            The validated rating value.

        Raises:
            InvalidRatingError: When the rating is not a multiple of 0.5.
        """
        if value is None:
            return value
        if round(value * 2) != value * 2:
            raise InvalidRatingError("Rating must be in increments of 0.5")
        return value

class CreateReview(BaseReview):
    """Request payload for creating a new review."""

class UpdateReview(BaseReview):
    """Request payload for updating an existing review."""

class GetReview(BaseModel):
    """Response payload representing a review."""

    id: int
    user_id: int
    username: str | None = None
    work_id: int
    work_title: str | None = None
    rating: float | None = None
    text: str | None = None
    contains_spoiler: bool
    created_at: datetime
    updated_at: datetime  | None = None

class CreateReviewComment(BaseModel):
    """Request payload for creating a comment on a review."""

    text: str = Field(max_length=1000)

class UpdateReviewComment(BaseModel):
    """Request payload for updating a review comment."""

    text: str = Field(max_length=1000)

class GetReviewComment(BaseModel):
    """Response payload representing a comment on a review."""

    id: int
    user_id: int
    username: str | None = None
    review_id: int
    text: str
    created_at: datetime
    updated_at: datetime


class GetReviewLike(BaseModel):
    """Response payload representing a like on a review."""

    id: int
    user_id: int
    username: str | None = None
    review_id: int

