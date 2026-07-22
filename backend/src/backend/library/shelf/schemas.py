from enum import Enum

from datetime import date, datetime

from pydantic import BaseModel, Field

class ShelfVisibility(str, Enum):
    public = "public"
    private = "private"
    followers_only = "followers_only"

class ShelfDefault(str, Enum):
    want_to_read = "want_to_read"
    currently_reading = "currently_reading"
    read = "read"
    did_not_finish = "did_not_finish"

class CreateShelf(BaseModel):
    name: str

class UpdateShelf(BaseModel):
    name: str

class UpdateShelfVisibility(BaseModel):
    visibility: ShelfVisibility

class GetShelf(BaseModel):
    id: int
    user_id: int
    name: str
    is_default: bool
    visibility: str
    created_at: datetime

class CreateShelfItem(BaseModel):
    work_id: int
    edition_id: int | None = None

class GetShelfItem(BaseModel):
    id: int
    shelf_id: int
    work_id: int
    edition_id: int | None
    created_at: datetime