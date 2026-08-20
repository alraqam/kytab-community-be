from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.trust_safety.export.managers import DataExportManager


async def get_data_export_manager(
        session: AsyncSession = Depends(get_db)
) -> DataExportManager:
    """Provides a DataExportManager bound to the request-scoped database session.

    Args:
        session: Database session injected via dependency.

    Returns:
        DataExportManager instance for the current request.
    """
    return DataExportManager(session)
