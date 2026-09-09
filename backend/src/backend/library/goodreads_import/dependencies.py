from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.library.goodreads_import.managers import GoodreadsImportManager
from src.backend.library.goodreads_import.models import GoodreadsImportRow


async def get_goodreads_import_manager(
        session: AsyncSession = Depends(get_db)
) -> GoodreadsImportManager:
    """Builds a GoodreadsImportManager bound to the request's database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        GoodreadsImportManager instance.
    """
    return GoodreadsImportManager(session)

async def get_goodreads_import_row_or_404(
        row_id: int,
        manager: GoodreadsImportManager = Depends(get_goodreads_import_manager)
) -> GoodreadsImportRow:
    """Resolves an import row from the path parameter or raises a 404.

    Args:
        row_id: ID of the import row to fetch.
        manager: GoodreadsImportManager used to look up the row.

    Returns:
        Matching GoodreadsImportRow instance.

    Raises:
        GoodreadsImportRowNotFoundError: When no import row matches the ID.
    """
    return await manager.get_row_by_id(row_id)
