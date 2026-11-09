from src.backend.core.exceptions import Conflict, NotFound, Forbidden


class DateInPastError(Conflict):
    """Raised when a provided deadline or closing date is in the past."""


class ActiveSessionError(Conflict):
    """Raised when an operation requires an active session but the session is not active, or vice versa."""


class ReadingSessionNotFound(NotFound):
    """Raised when a reading session with the given ID does not exist."""

class ActiveSessionNotFoundError(NotFound):
    """Raised when no active reading session exists for the club."""

class MaxActiveSessionsError(Conflict):
    """Raised when a club already has the maximum number of active reading sessions."""

class MilestoneAlreadyExistsError(Conflict):
    """Raised when a milestone with the same boundary type and value already exists for the session."""

class MilestoneNotFoundError(NotFound):
    """Raised when a milestone with the given ID does not exist."""

class MilestoneValueError(Conflict):
    """Raised when a milestone's boundary value is invalid for its boundary type."""

class IsNotProgressOwner(Forbidden):
    """Raised when a user attempts to act on a milestone progress record they do not own."""

class MilestoneProgressNotFound(NotFound):
    """Raised when a milestone progress record with the given ID does not exist."""

class MilestoneProgressAlreadyExists(Conflict):
    """Raised when a milestone progress record already exists for the session and user."""

class  ReadingSessionNotInClubError(NotFound):
    """Raised when a reading session does not belong to the given club."""

class  MilestoneNotInReadingSessionError(NotFound):
    """Raised when a milestone does not belong to the given reading session."""

class  ProgressNotInMilestone(NotFound):
    """Raised when a milestone progress record does not belong to the given milestone."""

class DiscussionPromptNotFoundError(NotFound):
    """Raised when a discussion prompt with the given ID does not exist."""

class PromptNotInMilestoneError(NotFound):
    """Raised when a discussion prompt does not belong to the given milestone."""