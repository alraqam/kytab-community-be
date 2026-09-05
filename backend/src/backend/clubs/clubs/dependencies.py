from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.models import Club
from src.backend.core.dependencies import get_db, get_storage_service
from src.backend.core.storage import StorageService

from src.backend.clubs.clubs.managers import ClubManager

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