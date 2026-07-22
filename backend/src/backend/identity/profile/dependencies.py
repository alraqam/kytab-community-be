from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.identity.profile.managers import ProfileManager

async def get_profile_manager(
        session: AsyncSession = Depends(get_db)
) -> ProfileManager:
    """FastAPI dependency that provides a ProfileManager instance.

    Args:
        session: Async SQLAlchemy session injected by get_db.

    Returns:
        ProfileManager bound to the current session.
    """
    return ProfileManager(session)