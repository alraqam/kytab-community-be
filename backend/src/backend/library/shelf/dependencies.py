from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.exceptions import ShelfItemNotInShelfError
from src.backend.core.dependencies import get_db
from src.backend.library.shelf.models import Shelf, ShelfItem


from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.managers.shelf_item import ShelfItemManager


async def get_shelf_manager(
        session: AsyncSession = Depends(get_db)
) -> ShelfManager:
    """Builds a ShelfManager bound to the request's database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        ShelfManager instance.
    """
    return ShelfManager(session)

async def get_shelf_or_404(
        shelf_id: int,
        manager: ShelfManager = Depends(get_shelf_manager)
) -> Shelf:
    """Resolves a shelf from the path parameter or raises a 404.

    Args:
        shelf_id: ID of the shelf to fetch.
        manager: ShelfManager used to look up the shelf.

    Returns:
        Matching Shelf instance.

    Raises:
        ShelfNotFoundError: When no shelf matches the ID.
    """
    return await manager.get_shelf_by_id(shelf_id)


async def get_shelf_item_manager(
        session: AsyncSession = Depends(get_db)
) -> ShelfItemManager:
    """Builds a ShelfItemManager bound to the request's database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        ShelfItemManager instance.
    """
    return ShelfItemManager(session)

async def get_shelf_item_or_404(
        shelf_item_id: int,
        shelf: Shelf = Depends(get_shelf_or_404),
        manager: ShelfItemManager = Depends(get_shelf_item_manager)
) -> ShelfItem:
    """Resolves a shelf item from the path parameter, scoped to its parent shelf.

    Args:
        shelf_item_id: ID of the shelf item to fetch.
        shelf: Parent Shelf the item must belong to.
        manager: ShelfItemManager used to look up the shelf item.

    Returns:
        Matching ShelfItem instance.

    Raises:
        ShelfItemNotFoundError: When no shelf item matches the ID.
        ShelfItemNotInShelfError: When the shelf item belongs to a different shelf.
    """
    shelf_item = await manager.get_shelf_item_by_id(shelf_item_id)
    if shelf_item.shelf_id != shelf.id:
        raise ShelfItemNotInShelfError("Shelf item not found in this shelf")
    return shelf_item