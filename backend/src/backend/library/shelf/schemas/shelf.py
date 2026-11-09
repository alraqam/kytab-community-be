from enum import Enum

from datetime import date, datetime

from pydantic import BaseModel, Field

class ShelfVisibility(str, Enum):
    """Enumeration of who may view a shelf."""

    public = "public"
    private = "private"
    followers_only = "followers_only"

class ShelfDefault(str, Enum):
    """Enumeration of the default shelf names created for every new user."""

    want_to_read = "want_to_read"
    currently_reading = "currently_reading"
    read = "read"
    did_not_finish = "did_not_finish"

class CreateShelf(BaseModel):
    """Request payload for creating a new custom shelf."""

    name: str

class UpdateShelf(BaseModel):
    """Request payload for renaming a shelf."""

    name: str

class UpdateShelfVisibility(BaseModel):
    """Request payload for changing a shelf's visibility setting."""

    visibility: ShelfVisibility

class GetShelf(BaseModel):
    """Response payload representing a shelf."""

    id: int
    user_id: int
    username: str | None = None
    name: str
    is_default: bool
    visibility: str
    created_at: datetime

class CreateShelfItem(BaseModel):
    """Request payload for adding a work, and optionally a specific edition, to a shelf."""

    work_id: int
    edition_id: int | None = None

class UpdateShelfItemEdition(BaseModel):
    """Request payload for setting a shelf item's preferred edition."""

    edition_id: int | None = None

class GetShelfItem(BaseModel):
    """Response payload representing an item placed on a shelf."""

    id: int
    shelf_id: int
    work_id: int
    work_title: str | None = None
    edition_id: int | None
    edition_title: str | None = None
    created_at: datetime