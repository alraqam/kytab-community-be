from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.models import ShelfItem, Shelf


@dataclass
class ShelfItemRepository:
    """Data-access layer for shelf item persistence and queries."""

    session: AsyncSession

    async def add_to_shelf(
            self,
            shelf_id: int,
            work_id: int,
            edition_id: int | None = None
    ) -> ShelfItem:
        """Inserts a new shelf item.

        Args:
            shelf_id: ID of the shelf the item belongs to.
            work_id: ID of the work being added.
            edition_id: ID of the specific edition, or None if unspecified.

        Returns:
            Newly created ShelfItem instance.
        """
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
        """Deletes a shelf item.

        Args:
            shelf_item: ShelfItem instance to delete.
        """
        await self.session.delete(shelf_item)
        await self.session.flush()

    async def change_shelf(
            self,
            shelf_item: ShelfItem,
            shelf_id: int
    ) -> None:
        """Moves a shelf item to a different shelf.

        Args:
            shelf_item: ShelfItem instance to move.
            shelf_id: ID of the destination shelf.
        """
        shelf_item.shelf_id = shelf_id
        self.session.add(shelf_item)
        await self.session.flush()

    async def update_edition(
            self,
            shelf_item: ShelfItem,
            edition_id: int | None
    ) -> None:
        """Updates a shelf item's preferred edition.

        Args:
            shelf_item: ShelfItem instance to update.
            edition_id: ID of the new preferred edition, or None to clear it.
        """
        shelf_item.edition_id = edition_id
        self.session.add(shelf_item)
        await self.session.flush()

    async def get_shelf_items(
            self,
            shelf_id: int
    ) -> list[ShelfItem]:
        """Lists all items on a shelf.

        Args:
            shelf_id: ID of the shelf whose items are being listed.

        Returns:
            List of matching ShelfItem instances.
        """
        stmt = select(ShelfItem).where(ShelfItem.shelf_id == shelf_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_shelf_by_item(
            self,
            shelf_item_id: int
    ) -> Shelf | None:
        """Fetches the shelf that contains the given shelf item.

        Args:
            shelf_item_id: ID of the shelf item whose shelf is being fetched.

        Returns:
            Matching Shelf instance, or None if not found.
        """
        stmt = (
            select(Shelf)
            .join(ShelfItem, ShelfItem.shelf_id == Shelf.id)
            .where(ShelfItem.id == shelf_item_id)
        )
        result = await self.session.execute(stmt)
        lst = result.scalar_one_or_none()
        return lst

    async def exists_in_shelf(
            self,
            user_id: int,
            work_id: int,
    ) -> ShelfItem | None:
        """Checks whether a work is already present in any of a user's shelves.

        Args:
            user_id: ID of the user whose shelves are checked.
            work_id: ID of the work to look for.

        Returns:
            Matching ShelfItem instance, or None if the work is not shelved.
        """
        stmt = (
            select(ShelfItem)
            .join(Shelf, ShelfItem.shelf_id == Shelf.id)
            .where(and_(Shelf.user_id == user_id, ShelfItem.work_id == work_id))
        )
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        return item

    async def exists_in_default_shelf(
            self,
            user_id: int,
            work_id: int,
    ) -> ShelfItem | None:
        """Checks whether a work is already present in one of a user's default status shelves.

        Args:
            user_id: ID of the user whose shelves are checked.
            work_id: ID of the work to look for.

        Returns:
            Matching ShelfItem instance, or None if the work is not on a default shelf.
        """
        stmt = (
            select(ShelfItem)
            .join(Shelf, ShelfItem.shelf_id == Shelf.id)
            .where(and_(Shelf.user_id == user_id, ShelfItem.work_id == work_id, Shelf.is_default == True))
        )
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        return item

    async def get_shelf_item_by_id(
            self,
            shelf_item_id: int
    ) -> ShelfItem | None:
        """Fetches a single shelf item by ID.

        Args:
            shelf_item_id: ID of the shelf item to fetch.

        Returns:
            Matching ShelfItem instance, or None if not found.
        """
        stmt = select(ShelfItem).where(ShelfItem.id == shelf_item_id)
        result = await self.session.execute(stmt)
        shelf_item = result.scalar_one_or_none()
        return shelf_item

