from pydantic import BaseModel


class CreateFollow(BaseModel):
    followed_id: int

class GetFollow(BaseModel):
    follower_id: int
    followed_id: int