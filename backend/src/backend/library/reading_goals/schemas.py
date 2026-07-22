from datetime import datetime

from pydantic import BaseModel, Field


class CreateReadingGoal(BaseModel):
    year: int = Field(ge=1000, le=9999)
    target_count: int = Field(ge=1)

class UpdateReadingGoal(BaseModel):
    target_count: int = Field(ge=1)

class GetReadingGoal(BaseModel):
    id: int
    user_id: int
    year: int
    target_count: int
    created_at: datetime