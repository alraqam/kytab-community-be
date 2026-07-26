from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.backend.library.reviews.exceptions import InvalidRatingError


class BaseReview(BaseModel):
    rating: float| None = Field(ge=0.5, le=5.0)
    text: str | None = Field(max_length=5000)
    contains_spoiler: bool

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: float) -> float| None:
        if value is None:
            return value
        if round(value * 2) != value * 2:
            raise InvalidRatingError("Rating must be in increments of 0.5")
        return value

class CreateReview(BaseReview):
    pass

class UpdateReview(BaseReview):
    pass

class GetReview(BaseModel):
    id: int
    work_id: int
    rating: float | None = None
    text: str | None = None
    contains_spoiler: bool
    created_at: datetime
    updated_at: datetime  | None = None

class CreateReviewComment(BaseModel):
    text: str = Field(max_length=1000)

class UpdateReviewComment(BaseModel):
    text: str = Field(max_length=1000)

class GetReviewComment(BaseModel):
    id: int
    user_id: int
    review_id: int
    text: str
    created_at: datetime
    updated_at: datetime


class GetReviewLike(BaseModel):
    id: int
    user_id: int
    review_id: int

