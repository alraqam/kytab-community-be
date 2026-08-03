from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.models import Shelf


@dataclass
class ShelfRepository:
    """Data-access layer for shelf persistence and queries."""

    session: AsyncSession

    async def create_shelf(
            self,
            user_id: int,
            name: str,
            is_default: bool,
            visibility: str,
    ) -> Shelf:
        """Inserts a new shelf.

        Args:
            user_id: ID of the user who owns the shelf.
            name: Shelf name.
            is_default: Whether the shelf is one of the user's default shelves.
            visibility: Visibility setting for the shelf.

        Returns:
            Newly created Shelf instance.
        """
        result = Shelf(
            user_id=user_id,
            name=name,
            is_default=is_default,
            visibility=visibility,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_shelf(
            self,
            shelf: Shelf,
            name: str
    ) -> None:
        """Renames a shelf.

        Args:
            shelf: Shelf instance to update.
            name: New shelf name.
        """
        shelf.name = name
        self.session.add(shelf)
        await self.session.flush()

    async def update_shelf_visibility(
            self,
            shelf: Shelf,
            visibility: str
    ) -> None:
        """Updates a shelf's visibility setting.

        Args:
            shelf: Shelf instance to update.
            visibility: New visibility value.
        """
        shelf.visibility = visibility
        self.session.add(shelf)
        await self.session.flush()

    async def delete_shelf(
            self,
            shelf: Shelf,
    ) -> None:
        """Deletes a shelf.

        Args:
            shelf: Shelf instance to delete.
        """
        await self.session.delete(shelf)
        await self.session.flush()

    async def get_user_shelves(
            self,
            user_id: int
    ) -> list[Shelf]:
        """Lists all shelves owned by a user.

        Args:
            user_id: ID of the user whose shelves are being listed.

        Returns:
            List of matching Shelf instances.
        """
        stmt = select(Shelf).where(Shelf.user_id == user_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_shelf_by_id(
            self,
            shelf_id: int
    ) -> Shelf | None:
        """Fetches a single shelf by ID.

        Args:
            shelf_id: ID of the shelf to fetch.

        Returns:
            Matching Shelf instance, or None if not found.
        """
        stmt = select(Shelf).where(Shelf.id == shelf_id)
        result = await self.session.execute(stmt)
        shelf = result.scalar_one_or_none()
        return shelf

    async def get_shelf_by_name(
            self,
            user_id: int,
            name: str
    ) -> Shelf | None:
        """Fetches a user's shelf by name.

        Args:
            user_id: ID of the user who owns the shelf.
            name: Name of the shelf to fetch.

        Returns:
            Matching Shelf instance, or None if not found.
        """
        stmt = select(Shelf).where(
            and_(
                Shelf.name == name,
                Shelf.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        shelf = result.scalar_one_or_none()
        return shelf
