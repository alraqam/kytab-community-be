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
    """Handles business logic for starting, finishing, and retrieving reading periods."""

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
        """Verifies that the user owns the shelf backing a reading period.

        Args:
            user: User to check.
            reading_period: ReadingPeriod whose owning shelf is checked.

        Returns:
            The Shelf that owns the reading period.

        Raises:
            ShelfNotFoundError: When no shelf is found for the reading period.
            IsNotShelfOwnerError: When the user does not own the shelf.
        """
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
        """Starts a new reading period for a shelf item and moves it to the "currently reading" shelf.

        Args:
            user: User starting the reading period; must own the shelf.
            shelf_item: ShelfItem to start reading.

        Returns:
            Newly created ReadingPeriod instance.

        Raises:
            ShelfNotFoundError: When the shelf backing the shelf item, or the user's
                "currently reading" shelf, cannot be found.
            IsNotShelfOwnerError: When the user does not own the shelf.
            ActiveReadingPeriodError: When an active reading period already exists for this work.
        """
        shelf = await self.shelf_item_manager.get_shelf_by_item(shelf_item.id)
        await is_shelf_owner(user, shelf)

        exists = await self.reading_period_repo.exists_active_period(user.id, shelf_item.work_id)
        if exists:
            raise ActiveReadingPeriodError("Active reading period already exists")

        currently_reading = await self.shelf_manager.get_shelf_by_name(user, ShelfDefault.currently_reading)
        result = await self.reading_period_repo.start_reading_period(shelf_item.id)
        await self.shelf_item_manager.change_shelf(user, shelf_item, currently_reading)

        await self.session.commit()
        return await self.reading_period_repo.get_reading_period_by_id(result.id)

    async def set_finishing_date(
            self,
            user: User,
            reading_period: ReadingPeriod
    ) -> None:
        """Marks a reading period as finished and moves its shelf item to the "read" shelf.

        Args:
            user: User expected to own the reading period.
            reading_period: ReadingPeriod to mark finished.

        Raises:
            ShelfNotFoundError: When the owning shelf, the user's "read" shelf, or
                the shelf item cannot be found.
            IsNotShelfOwnerError: When the user does not own the shelf.
        """
        await self.is_reading_period_owner(user, reading_period)

        read = await self.shelf_manager.get_shelf_by_name(user, ShelfDefault.read)

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
        """Deletes a reading period, for the owning user.

        Args:
            user: User expected to own the reading period.
            reading_period: ReadingPeriod to delete.

        Raises:
            ShelfNotFoundError: When the shelf backing the reading period cannot be found.
            IsNotShelfOwnerError: When the user does not own the shelf.
        """
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
        """Lists all reading periods belonging to the given user.

        Args:
            user: User whose reading periods are listed.

        Returns:
            List of matching ReadingPeriod instances.
        """
        result = await self.reading_period_repo.get_user_reading_periods(user.id)
        return result

    async def get_shelf_item_periods(
            self,
            shelf_item: ShelfItem,
    ) -> list[ReadingPeriod]:
        """Lists all reading periods for a shelf item.

        Args:
            shelf_item: ShelfItem to list reading periods for.

        Returns:
            List of matching ReadingPeriod instances.
        """
        result = await self.reading_period_repo.get_shelf_item_periods(shelf_item.id)
        return result

    async def get_reading_period_by_id(
            self,
            reading_period: int,
    ) -> ReadingPeriod:
        """Fetches a reading period by ID.

        Args:
            reading_period: ID of the reading period to fetch.

        Returns:
            Matching ReadingPeriod instance.

        Raises:
            ReadingPeriodNotFound: When no reading period matches the ID.
        """
        result = await self.reading_period_repo.get_reading_period_by_id(reading_period)
        if not result:
            raise ReadingPeriodNotFound("Reading period not found")
        return result

    async def get_edition_by_reading_period(
            self,
            reading_period: ReadingPeriod
    ):
        """Fetches the edition associated with a reading period's shelf item, if any.

        Args:
            reading_period: ReadingPeriod to look up the edition for.

        Returns:
            Matching Edition instance, or None if not found.
        """
        result = await self.reading_period_repo.get_edition_by_reading_period(reading_period.id)
        return result

    async def get_user_reading_periods(
            self,
            user: User,
            current_user: User,
            shelf: Shelf
    ) -> list[ReadingPeriod]:
        """Lists a user's reading periods, enforcing shelf visibility rules for the requester.

        Args:
            user: User whose reading periods are listed.
            current_user: User making the request.
            shelf: Shelf used to check visibility access.

        Returns:
            List of matching ReadingPeriod instances.

        Raises:
            PrivateShelfError: When the current user is not permitted to view the shelf.
        """
        await self.shelf_manager.ensure_shelf_access(shelf, current_user, user)
        periods = await self.reading_period_repo.get_user_reading_periods(user.id)
        return periods