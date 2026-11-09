from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.identity.auth.schemas.auth import UserRoleEnum, STAFF_ROLES
from src.backend.identity.users.exceptions.user import PermissionDeniedError
from src.backend.identity.users.managers.user import UserManager


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

async def is_staff(
        user: User = Depends(get_current_user)
) -> User:
    """FastAPI dependency that verifies the current user is platform staff (admin or platform moderator).

    Use for moderation and day-to-day operations (announcements, club enforcement,
    complaints, content removal). Keep `is_admin` for role management, configuration,
    and other admin-only actions.

    Args:
        user: Currently authenticated user injected by get_current_user.

    Returns:
        User instance if they are an admin or platform moderator.

    Raises:
        PermissionDeniedError: When the current user is neither an admin nor a platform moderator.
    """
    if user.role not in STAFF_ROLES:
        raise PermissionDeniedError("Permission denied")
    return user

def ensure_can_moderate_user(
        actor: User,
        target: User,
) -> None:
    """Verifies that a staff member may take an enforcement action against another user.

    Admins may act on anyone. Platform moderators may not act on staff accounts
    (admins or other platform moderators).

    Args:
        actor: Staff member performing the action.
        target: User the action applies to.

    Raises:
        PermissionDeniedError: When a platform moderator targets a staff account.
    """
    if actor.role != UserRoleEnum.admin and target.role in STAFF_ROLES:
        raise PermissionDeniedError("Platform moderators cannot act on staff accounts")

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
