from datetime import datetime

from pydantic import BaseModel, Field


class CreateReadingGoal(BaseModel):
    """Request payload for creating a new reading goal."""

    year: int = Field(ge=1000, le=9999)
    target_count: int = Field(ge=1)

class UpdateReadingGoal(BaseModel):
    """Request payload for updating a reading goal's target count."""

    target_count: int = Field(ge=1)

class GetReadingGoal(BaseModel):
    """Response payload representing a reading goal."""

    id: int
    user_id: int
    year: int
    target_count: int
    created_at: datetime