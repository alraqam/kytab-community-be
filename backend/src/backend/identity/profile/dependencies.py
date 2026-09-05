from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db, get_storage_service
from src.backend.core.storage import StorageService
from src.backend.identity.profile.managers import ProfileManager

async def get_profile_manager(
        session: AsyncSession = Depends(get_db),
        storage: StorageService = Depends(get_storage_service),
) -> ProfileManager:
    """FastAPI dependency that provides a ProfileManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.
        storage: StorageService injected by get_storage_service.

    Returns:
        ProfileManager bound to the current session.
    """
    return ProfileManager(session, storage)