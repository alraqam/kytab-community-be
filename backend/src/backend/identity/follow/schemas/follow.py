from pydantic import BaseModel


class CreateFollow(BaseModel):
    """Request payload for following another user."""

    followed_id: int

class GetFollow(BaseModel):
    """Response payload representing a follow relationship between two users."""

    follower_id: int
    follower_username: str | None = None
    followed_id: int
    followed_username: str | None = None