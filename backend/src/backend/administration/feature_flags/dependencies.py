from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.feature_flags.managers import FeatureFlagManager
from src.backend.administration.feature_flags.models import FeatureFlag
from src.backend.core.dependencies import get_db


async def get_feature_flag_manager(
        session: AsyncSession = Depends(get_db)
) -> FeatureFlagManager:
    """Builds a FeatureFlagManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        FeatureFlagManager instance.
    """
    return FeatureFlagManager(session)

async def get_feature_flag_or_404(
        flag_id: int,
        manager: FeatureFlagManager = Depends(get_feature_flag_manager)
) -> FeatureFlag:
    """Resolves a feature flag by path parameter or raises if it doesn't exist.

    Args:
        flag_id: ID of the feature flag from the path.
        manager: FeatureFlagManager used to look up the feature flag.

    Returns:
        FeatureFlag instance.

    Raises:
        FeatureFlagNotFoundError: When no feature flag matches the ID.
    """
    return await manager.get_feature_flag_by_id(flag_id)
