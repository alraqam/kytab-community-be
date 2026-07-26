from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.dependencies import get_db
from src.backend.library.shelf.models import Shelf, ShelfItem


from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.managers.shelf_item import ShelfItemManager


async def get_shelf_manager(
        session: AsyncSession = Depends(get_db)
) -> ShelfManager:
    return ShelfManager(session)

async def get_shelf_or_404(
        shelf_id: int,
        manager: ShelfManager = Depends(get_shelf_manager)
) -> Shelf:
    return await manager.get_shelf_by_id(shelf_id)


async def get_shelf_item_manager(
        session: AsyncSession = Depends(get_db)
) -> ShelfItemManager:
    return ShelfItemManager(session)

async def get_shelf_item_or_404(
        shelf_item_id: int,
        manager: ShelfItemManager = Depends(get_shelf_item_manager)
) -> ShelfItem:
    return await manager.get_shelf_item_by_id(shelf_item_id)