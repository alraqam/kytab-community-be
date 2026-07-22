from datetime import datetime

from pydantic import BaseModel


class TimeActionSchema(BaseModel):
    """Base Pydantic schema providing optional created_at and updated_at timestamp fields."""

    created_at: datetime | None = None
    updated_at: datetime | None = None