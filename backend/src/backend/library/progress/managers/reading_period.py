from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.library.shelf.exceptions import IsNotShelfOwnerError
from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.managers.shelf_item import ShelfItemManager
from src.backend.library.shelf.schemas import ShelfDefault
from src.backend.library.shelf.exceptions import ShelfNotFoundError
from src.backend.identity.auth.models import User
from src.backend.library.progress.exceptions import ReadingPeriodNotFound, ActiveReadingPeriodError
from src.backend.library.progress.models import ReadingPeriod
from src.backend.library.shelf.permissions import is_shelf_owner
from src.backend.library.shelf.models import ShelfItem, Shelf
from src.backend.library.progress.repositories.reading_period import ReadingPeriodRepository


class ReadingPeriodManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.reading_period_repo = ReadingPeriodRepository(session)
        self.shelf_item_manager = ShelfItemManager(session)

        self.shelf_manager = ShelfManager(session)

    async def is_reading_period_owner(
            self,
            user: User,
            reading_period: ReadingPeriod
    ):
        shelf = await self.reading_period_repo.get_shelf_by_period(reading_period.id)
        if not shelf:
            raise ShelfNotFoundError("Shelf not found")

        if shelf.user_id != user.id:
            raise IsNotShelfOwnerError("Is not shelf owner")
        return shelf


    async def start_reading_period(
            self,
            user: User,
            shelf_item: ShelfItem
    ) -> ReadingPeriod:
        shelf = await self.shelf_item_manager.get_shelf_by_item(shelf_item.id)
        await is_shelf_owner(user, shelf)

        exists = await self.reading_period_repo.exists_active_period(user.id, shelf_item.work_id)
        if exists:
            raise ActiveReadingPeriodError("Active reading period already exists")

        currently_reading = await self.shelf_manager.get_shelf_by_name(user.id, ShelfDefault.currently_reading)
        result = await self.reading_period_repo.start_reading_period(shelf_item.id)
        await self.shelf_item_manager.change_shelf(user, shelf_item, currently_reading)

        await self.session.commit()
        return result

    async def set_finishing_date(
            self,
            user: User,
            reading_period: ReadingPeriod
    ) -> None:
        await self.is_reading_period_owner(user, reading_period)

        read = await self.shelf_manager.get_shelf_by_name(user.id, ShelfDefault.currently_reading)

        shelf_item = await self.reading_period_repo.get_shelf_item_by_period(reading_period.id)
        if not shelf_item:
            raise ShelfNotFoundError("Shelf not found")

        await self.reading_period_repo.set_finishing_date(reading_period)
        await self.shelf_item_manager.change_shelf(user, shelf_item, read)
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

    async def get_my_reading_periods(
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

    async def get_edition_by_reading_period(
            self,
            reading_period: ReadingPeriod
    ):
        result = await self.reading_period_repo.get_edition_by_reading_period(reading_period.id)
        return result

    async def get_user_reading_periods(
            self,
            user: User,
            current_user: User,
            shelf: Shelf
    ) -> list[ReadingPeriod]:
        await self.shelf_manager.ensure_shelf_access(shelf, current_user, user)
        periods = await self.reading_period_repo.get_user_reading_periods(user.id)
        return periods