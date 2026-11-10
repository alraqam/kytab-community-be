from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.permissions.membership import ensure_staff_club_access
from src.backend.clubs.clubs.models.club import Club
from src.backend.identity.auth.models.auth import User
from src.backend.identity.users.dependencies.user import is_staff
from src.backend.core.dependencies import get_db, get_storage_service
from src.backend.core.storage import StorageService

from src.backend.clubs.clubs.managers.club import ClubManager

async def get_club_manager(
        session: AsyncSession = Depends(get_db),
        storage: StorageService = Depends(get_storage_service),
) -> ClubManager:
    """Builds a ClubManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.
        storage: StorageService injected by get_storage_service.

    Returns:
        ClubManager instance.
    """
    return ClubManager(session, storage)

async def get_club_or_404(
        club_id: int,
        manager: ClubManager = Depends(get_club_manager)
) -> Club:
    """Resolves a club by path parameter or raises if it doesn't exist.

    Args:
        club_id: ID of the club from the path.
        manager: ClubManager used to look up the club.

    Returns:
        Club instance.

    Raises:
        ClubNotFoundError: When no club matches the ID.
    """
    return await manager.get_club_by_id(club_id)

async def get_managed_club_or_404(
        club: Club = Depends(get_club_or_404),
        user: User = Depends(is_staff),
) -> Club:
    """Resolves a club for a staff route, restricting platform moderators to their assigned clubs.

    Args:
        club: Club resolved from the path by get_club_or_404.
        user: Current staff user (admin or platform moderator) injected by is_staff.

    Returns:
        Club instance.

    Raises:
        ClubNotFoundError: When no club matches the ID.
        PermissionDeniedError: When the user is not staff, or is a platform moderator the club is not assigned to.
    """
    ensure_staff_club_access(club, user)
    return club
