from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator

from backend.library.reviews.exceptions import InvalidRatingError


class BaseReview(BaseModel):
    rating: int = Field(ge=0.5, le=5.0)
    text: str = Field(max_length=5000)
    contains_spoiler: bool

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: str) -> str:
        if not value % 5 != 0:
            raise InvalidRatingError("Invalid rating")
        return value


class CreateReview(BaseReview):
    pass

class UpdateReview(BaseReview):
    pass

class GetReview(BaseModel):
    id: int
    work_id: int
    rating: int | None = None
    text: str | None = None
    contains_spoiler: bool
    created_at: datetime
    updated_at: datetime  | None = None

