from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.models import Shelf


@dataclass
class ShelfRepository:
    session: AsyncSession

    async def create_shelf(
            self,
            user_id: int,
            name: str,
            is_default: bool,
            visibility: str,
    ) -> Shelf:
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
        shelf.name = name
        self.session.add(shelf)
        await self.session.flush()

    async def delete_shelf(
            self,
            shelf: Shelf,
    ) -> None:
        await self.session.delete(shelf)
        await self.session.flush()

    async def get_user_shelves(
            self,
            user_id: int
    ) -> list[Shelf]:
        stmt = select(Shelf).where(Shelf.user_id == user_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_shelf_by_id(
            self,
            shelf_id: int
    ) -> Shelf | None:
        stmt = select(Shelf).where(Shelf.id == shelf_id)
        result = await self.session.execute(stmt)
        shelf = result.scalar_one_or_none()
        return shelf

    async def get_shelf_by_name(
            self,
            user_id: int,
            name: str
    ) -> Shelf | None:
        stmt = select(Shelf).where(
            and_(
                Shelf.name == name,
                Shelf.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        shelf = result.scalar_one_or_none()
        return shelf
