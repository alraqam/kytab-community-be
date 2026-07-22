from pydantic import BaseModel


class CreateBlock(BaseModel):
    blocked_id: int

class GetBlocked(BaseModel):
    id: int
    blocker_id: int
    blocked_id: int