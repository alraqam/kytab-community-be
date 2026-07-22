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
    if user.role != UserRoleEnum.librarian:
        raise PermissionDeniedError("Permission denied")
    return user

async def get_librarian_submission_manager(
        session: AsyncSession = Depends(get_db)
) -> LibrarianSubmissionManager:
    return LibrarianSubmissionManager(session)

async def get_librarian_submission_or_404(
        submission_id: int,
        manager: LibrarianSubmissionManager = Depends(get_librarian_submission_manager)
) -> LibrarianSubmission:
    return await manager.get_submission_by_id(submission_id)