from datetime import datetime

from pydantic import BaseModel


class CreateThread(BaseModel):
    title: str

class UpdateThread(BaseModel):
    title: str

class GetThread(BaseModel):
    id: int
    session_id: int | None = None
    milestone_id: int | None = None
    is_general: bool
    title: str
    created_by_id: int
    is_locked: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime