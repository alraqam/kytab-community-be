from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class VotingStatus(str, Enum):
    """Possible statuses of a voting poll: active or closed."""

    active = "active"
    closed = "closed"

class CreateVotingPoll(BaseModel):
    """Request payload for creating a new voting poll with a closing datetime."""

    closes_at: datetime

class UpdateVotingPoll(BaseModel):
    """Request payload for updating the closing datetime of an existing poll."""

    closes_at: datetime

class GetVotingPoll(BaseModel):
    """Voting poll data returned in API responses."""

    id: int
    club_id: int
    created_by_id: int
    closes_at: datetime
    status: str
    created_at: datetime
    updated_at: datetime

class CreatePollCandidate(BaseModel):
    """Request payload for nominating a work as a candidate in a poll."""

    work_id: int

class GetPollCandidate(BaseModel):
    """Poll candidate data returned in API responses."""

    id: int
    poll_id: int
    work_id: int

class CreatePollVote(BaseModel):
    """Request payload for casting a vote for a poll candidate."""

    candidate_id: int

class GetPollVote(BaseModel):
    """Poll vote data returned in API responses."""

    id: int
    poll_id: int
    user_id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

class GetPollResult(BaseModel):
    """Vote count per candidate returned from the poll results endpoint."""

    candidate_id: int
    work_id: int
    vote_count: int