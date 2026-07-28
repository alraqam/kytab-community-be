from src.backend.core.exceptions import Forbidden, Conflict, NotFound, BadRequest


class IsNotClubOwnerError(Forbidden):
    """Raised when a non-owner/moderator attempts a privileged club operation."""


class AlreadyClubMemberError(Conflict):
    """Raised when a user tries to join a club they already belong to."""


class NotClubMemberError(Conflict):
    """Raised when an operation requires club membership but the user is not a member."""


class InvitationNotFoundError(NotFound):
    """Raised when an invitation with the given ID does not exist."""


class UnavailableInvitationError(BadRequest):
    """Raised when an invitation is expired or not in pending status."""


class UnavailableRequestError(BadRequest):
    """Raised when a join request is expired or not in pending status."""


class JoinRequestNotFound(NotFound):
    """Raised when a join request with the given ID does not exist."""

class ExpiredInvitationError(BadRequest):
    pass

class ExpiredRequestError(BadRequest):
    pass

class MemberAlreadyBlockedError(Conflict):
    pass

class ClubBlockNotFoundError(NotFound):
    pass

class ClubModeratorError(Conflict):
    pass

class ClubOwnerError(Conflict):
    pass

class PrivateClubError(Conflict):
    pass

class MemberBlockedError(Conflict):
    pass