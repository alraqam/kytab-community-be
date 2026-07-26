from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.exceptions import ShelfNotFoundError
from src.backend.identity.auth.models import User
from src.backend.library.progress.exceptions import ReadingPeriodNotFound
from src.backend.library.progress.models import ReadingPeriod
from src.backend.library.shelf.permissions import is_shelf_owner
from src.backend.library.shelf.exceptions import IsNotShelfOwnerError
from src.backend.library.shelf.models import ShelfItem
from src.backend.library.progress.repositories.reading_period import ReadingPeriodRepository
from src.backend.library.shelf.repositories.shelf_item import ShelfItemRepository


class ReadingPeriodManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.reading_period_repo = ReadingPeriodRepository(session)
        self.shelf_item_repo = ShelfItemRepository(session)

    async def start_reading_period(
            self,
            user: User,
            shelf_item: ShelfItem
    ) -> ReadingPeriod:
        shelf = await self.shelf_item_repo.get_shelf_by_item(shelf_item.id)
        if shelf.user_id == user.id:
            raise IsNotShelfOwnerError("Is not shelf owner")

        result = await self.reading_period_repo.start_reading_period(shelf_item.id)
        await self.session.commit()
        return result

    async def set_finishing_date(
            self,
            user: User,
            reading_period: ReadingPeriod
    ) -> None:
        shelf = await self.reading_period_repo.get_shelf_by_period(reading_period.id)
        if not shelf:
            raise ShelfNotFoundError("Shelf not found")
        await is_shelf_owner(user, shelf)

        await self.reading_period_repo.set_finishing_date(reading_period)
        await self.session.commit()

    async def delete_reading_period(
            self,
            user: User,
            reading_period: ReadingPeriod
    ) -> None:
        shelf = await self.reading_period_repo.get_shelf_by_period(reading_period.id)
        if not shelf:
            raise ShelfNotFoundError("Shelf not found")
        await is_shelf_owner(user, shelf)

        await self.reading_period_repo.delete_reading_period(reading_period)
        await self.session.commit()

    async def get_user_reading_periods(
            self,
            user: User,
    ) -> list[ReadingPeriod]:
        result = await self.reading_period_repo.get_user_reading_periods(user.id)
        return result

    async def get_shelf_item_periods(
            self,
            shelf_item: ShelfItem,
    ) -> list[ReadingPeriod]:
        result = await self.reading_period_repo.get_shelf_item_periods(shelf_item.id)
        return result

    async def get_reading_period_by_id(
            self,
            reading_period: int,
    ) -> ReadingPeriod:
        result = await self.reading_period_repo.get_reading_period_by_id(reading_period)
        if not result:
            raise ReadingPeriodNotFound("Reading period not found")
        return result