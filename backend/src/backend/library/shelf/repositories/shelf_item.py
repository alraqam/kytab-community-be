from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.models import ShelfItem, Shelf


@dataclass
class ShelfItemRepository:
    session: AsyncSession

    async def add_to_shelf(
            self,
            shelf_id: int,
            work_id: int,
            edition_id: int | None = None
    ) -> ShelfItem:
        result = ShelfItem(
            shelf_id=shelf_id,
            work_id=work_id,
            edition_id=edition_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def remove_from_shelf(
            self,
            shelf_item: ShelfItem,
    ) -> None:
        await self.session.delete(shelf_item)
        await self.session.flush()

    async def get_shelf_items(
            self,
            shelf_id: int
    ) -> list[ShelfItem]:
        stmt = select(ShelfItem).where(ShelfItem.shelf_id == shelf_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_shelf_by_item(
            self,
            shelf_item_id: int
    ) -> Shelf | None:
        stmt = (
            select(Shelf)
            .join(ShelfItem, ShelfItem.shelf_id == Shelf.id)
            .where(ShelfItem.id == shelf_item_id)
        )
        result = await self.session.execute(stmt)
        lst = result.scalar_one_or_none()
        return lst

    async def get_shelf_item_by_id(
            self,
            shelf_item_id: int
    ) -> ShelfItem | None:
        stmt = select(ShelfItem).where(ShelfItem.id == shelf_item_id)
        result = await self.session.execute(stmt)
        shelf_item = result.scalar_one_or_none()
        return shelf_item

