from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.progress.models import ReadingPeriod
from src.backend.library.shelf.models import Shelf, ShelfItem


@dataclass
class ReadingPeriodRepository:
    session: AsyncSession

    async def start_reading_period(
            self,
            shelf_item_id: int,
    ) -> ReadingPeriod:
        result = ReadingPeriod(
            shelf_item_id=shelf_item_id,
            started_at=datetime.now(),
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def set_finishing_date(
            self,
            reading_period: ReadingPeriod,
    ) -> None:
        reading_period.finished_at = datetime.now(),
        self.session.add(reading_period)
        await self.session.flush()

    async def delete_reading_period(
            self,
            reading_period: ReadingPeriod,
    ) -> None:
        await self.session.delete(reading_period)
        await self.session.flush()

    async def get_user_reading_periods(
            self,
            user_id: int
    ) -> list[ReadingPeriod]:
        stmt = select(ReadingPeriod).where(ReadingPeriod.user_id == user_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_shelf_item_periods(
            self,
            shelf_item: int
    ) -> list[ReadingPeriod]:
        stmt = select(ReadingPeriod).where(ReadingPeriod.shelf_item == shelf_item)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_reading_period_by_id(
            self,
            reading_period_id: int
    ) -> ReadingPeriod | None:
        stmt = select(ReadingPeriod).where(ReadingPeriod.id == reading_period_id)
        result = await self.session.execute(stmt)
        reading_period = result.scalar_one_or_none()
        return reading_period

    async def get_shelf_by_period(
            self,
            reading_period_id: int
    ) -> Shelf | None:
        stmt = (
            select(Shelf)
            .join(ShelfItem, ShelfItem.shelf_id == Shelf.id)
            .join(ReadingPeriod, ReadingPeriod.shelf_item_id == ShelfItem.id)
            .where(ReadingPeriod.id == reading_period_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

