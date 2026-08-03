from pydantic import BaseModel


class CreateBlock(BaseModel):
    """Request payload for blocking another user."""

    blocked_id: int

class GetBlocked(BaseModel):
    """Response payload representing a block relationship."""

    id: int
    blocker_id: int
    blocked_id: int