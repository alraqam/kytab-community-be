from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.core.dependencies import get_db
from src.backend.library.shelf.exceptions import IsNotShelfOwnerError
from src.backend.library.shelf.models import Shelf, ShelfItem


async def is_shelf_owner(
        user: User,
        shelf: Shelf,
) -> None:
    if shelf.user_id != user.id:
        raise IsNotShelfOwnerError("Only shelf owner can change their list")
    return

from src.backend.shelf.managers.shelf import ShelfManager

async def get_reading_list_manager(
        session: AsyncSession = Depends(get_db)
) -> ShelfManager:
    return ShelfManager(session)

async def get_shelf_or_404(
        shelf_id: int,
        manager: ShelfManager = Depends(get_reading_list_manager)
) -> Shelf:
    return await manager.get_shelf_by_id(shelf_id)


from src.backend.shelf.managers.shelf_item import ShelfItemManager

async def get_reading_list_manager(
        session: AsyncSession = Depends(get_db)
) -> ShelfItemManager:
    return ShelfItemManager(session)

async def get_shelf_item_or_404(
        shelf_item_id: int,
        manager: ShelfItemManager = Depends(get_reading_list_manager)
) -> ShelfItem:
    return await manager.get_shelf_item_by_id(shelf_item_id)