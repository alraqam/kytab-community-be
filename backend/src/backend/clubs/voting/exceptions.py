from src.backend.core.exceptions import Conflict, BadRequest, NotFound


class ActivePollAlreadyExistsError(Conflict):
    """Raised when trying to create a poll while one is already active in the club."""


class VotingClosedError(BadRequest):
    """Raised when an action requires an open poll but the poll is already closed."""


class ActivePollError(BadRequest):
    """Raised when trying to delete a poll that is still active."""


class ActivePollsNotFoundError(NotFound):
    """Raised when no active poll exists for the club."""


class PollNotFoundError(NotFound):
    """Raised when a voting poll with the given ID does not exist."""


class PollCandidateNotFound(NotFound):
    """Raised when a poll candidate with the given ID does not exist."""


class CandidateInPollError(Conflict):
    """Raised when the book is already registered as a candidate in the poll."""


class UserVoteExistsError(Conflict):
    """Raised when the user has already cast a vote in this poll."""


class PollVoteNotFoundError(NotFound):
    """Raised when a poll vote with the given ID does not exist."""

class PollNotInClubError(NotFound):
    pass