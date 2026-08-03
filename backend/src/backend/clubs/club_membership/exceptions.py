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
    """Raised when an invitation has expired."""

class ExpiredRequestError(BadRequest):
    """Raised when a join request has expired."""

class MemberAlreadyBlockedError(Conflict):
    """Raised when a user is already blocked from the club."""

class ClubBlockNotFoundError(NotFound):
    """Raised when a club block with the given ID does not exist."""

class ClubModeratorError(Conflict):
    """Raised when an operation on a club moderator's role is not permitted."""

class ClubOwnerError(Conflict):
    """Raised when an operation targeting the club owner is not permitted."""

class PrivateClubError(Conflict):
    """Raised when a user attempts to directly join a non-public club."""

class MemberBlockedError(Conflict):
    """Raised when a user blocked from the club attempts a club action."""

class DuplicateInvitationError(Conflict):
    """Raised when a pending invitation already exists for the target user."""

class InviteeEmailDisabledError(Conflict):
    """Raised when the invited user does not accept email invitations."""