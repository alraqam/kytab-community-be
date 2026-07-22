from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.identity.auth.schemas import UserRoleEnum
from src.backend.identity.users.exceptions import PermissionDeniedError
from src.backend.identity.users.managers import UserManager


async def is_admin(
        user: User = Depends(get_current_user)
) -> User:
    """FastAPI dependency that verifies the current user has the admin role.

    Args:
        user: Currently authenticated user injected by get_current_user.

    Returns:
        User instance if they are an admin.

    Raises:
        PermissionDeniedError: When the current user is not an admin.
    """
    if user.role != UserRoleEnum.admin:
        raise PermissionDeniedError("Permission denied")
    return user

async def get_user_manager(
        session: AsyncSession = Depends(get_db)
) -> UserManager:
    """FastAPI dependency that provides a UserManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        UserManager bound to the current session.
    """
    return UserManager(session)

async def get_user_or_404(
        user_id: int,
        manager: UserManager = Depends(get_user_manager)
) -> User:
    """FastAPI dependency that fetches a user by ID or raises if not found.

    Args:
        user_id: User ID from the path parameter.
        manager: UserManager injected by get_user_manager.

    Returns:
        User instance.

    Raises:
        UserNotFoundError: When no user with the given ID exists.
    """
    return await manager.get_user_by_id(user_id)
