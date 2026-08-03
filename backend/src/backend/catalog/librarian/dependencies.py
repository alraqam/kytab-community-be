from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.identity.auth.schemas import UserRoleEnum
from src.backend.core.dependencies import get_db
from src.backend.catalog.librarian.managers import LibrarianSubmissionManager
from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.identity.users.exceptions import PermissionDeniedError


async def is_librarian(
        user: User = Depends(get_current_user)
) -> User:
    """FastAPI dependency that restricts access to users with the librarian role.

    Args:
        user: Authenticated user injected by get_current_user.

    Returns:
        The authenticated User instance.

    Raises:
        PermissionDeniedError: When the user's role is not librarian.
    """
    if user.role != UserRoleEnum.librarian:
        raise PermissionDeniedError("Permission denied")
    return user

async def get_librarian_submission_manager(
        session: AsyncSession = Depends(get_db)
) -> LibrarianSubmissionManager:
    """FastAPI dependency that provides a LibrarianSubmissionManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        LibrarianSubmissionManager bound to the current session.
    """
    return LibrarianSubmissionManager(session)

async def get_librarian_submission_or_404(
        submission_id: int,
        manager: LibrarianSubmissionManager = Depends(get_librarian_submission_manager)
) -> LibrarianSubmission:
    """FastAPI dependency that fetches a librarian submission by ID or raises if not found.

    Args:
        submission_id: Submission ID from the path parameter.
        manager: LibrarianSubmissionManager injected by get_librarian_submission_manager.

    Returns:
        LibrarianSubmission instance.

    Raises:
        LibrarianSubmissionNotFoundError: When no submission with the given ID exists.
    """
    return await manager.get_submission_by_id(submission_id)