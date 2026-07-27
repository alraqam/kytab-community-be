from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.catalog.books.exceptions import InvalidWorkEditionError
from backend.catalog.books.managers.edition import EditionManager
from backend.catalog.books.managers.work import WorkManager
from backend.identity.follow.managers import FollowManager
from backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.exceptions import IsNotShelfOwnerError, ShelfNotFoundError, WorkAlreadyInShelfError
from src.backend.identity.auth.models import User
from src.backend.library.shelf.permissions import is_shelf_owner
from src.backend.library.shelf.exceptions import PrivateShelfError, ShelfItemNotFoundError
from src.backend.library.shelf.models import Shelf, ShelfItem
from src.backend.library.shelf.repositories.shelf_item import ShelfItemRepository
from src.backend.library.shelf.schemas import CreateShelfItem, ShelfVisibility


class ShelfItemManager:
    def __init__(
            self,
            session: AsyncSession
    ):

        self.session = session
        self.shelf_item_repo = ShelfItemRepository(session)
        self.follow_manager = FollowManager(session)
        self.work_manager = WorkManager(session)
        self.edition_manager = EditionManager(session)
        self.shelf_manager = ShelfManager(session)


    async def add_to_shelf(
            self,
            user: User,
            shelf: Shelf,
            request: CreateShelfItem
    ) -> ShelfItem:
        await is_shelf_owner(user, shelf)

        work = await self.work_manager.get_work_by_id(request.work_id)
        edition = await self.edition_manager.get_edition_by_id(request.edition_id) if request.edition_id else None

        if edition and edition.work_id != work.id:
            raise InvalidWorkEditionError("Invalid work edition")

        try:
            result = await self.shelf_item_repo.add_to_shelf(
                shelf_id=shelf.id,
                work_id=work.id,
                edition_id=edition.id if edition else None,
            )
            await self.session.commit()
            return result
        except IntegrityError:
            raise WorkAlreadyInShelfError("Work is already added to shelf")

    async def remove_from_shelf(
            self,
            user: User,
            shelf_item: ShelfItem,
    ) -> None:
        shelf = await self.shelf_item_repo.get_shelf_by_item(shelf_item.id)
        if not shelf:
            raise ShelfNotFoundError("Shelf not found")

        await is_shelf_owner(user, shelf)

        result = await self.shelf_item_repo.remove_from_shelf(
            shelf_item=shelf_item
        )
        await self.session.commit()
        return result

    async def change_shelf(
            self,
            user: User,
            shelf_item: ShelfItem,
            shelf: Shelf
    ) -> None:
        await is_shelf_owner(user, shelf)

        result = await self.shelf_item_repo.change_shelf(
            shelf_item=shelf_item,
            shelf_id=shelf.id
        )
        await self.session.commit()
        return result

    async def get_user_shelf_items(
            self,
            user: User,
            current_user: User,
            shelf: Shelf
    ) -> list[ShelfItem]:
        await self.shelf_manager.ensure_shelf_access(shelf, current_user, user)
        items = await self.shelf_item_repo.get_shelf_items(shelf.id)
        return items

    async def get_my_shelf_items(
            self,
            user: User,
            shelf: Shelf
    ) -> list[ShelfItem]:
        if user.id != shelf.user_id:
            raise IsNotShelfOwnerError("Is not shelf owner")
        items = await self.shelf_item_repo.get_shelf_items(shelf.id)
        return items

    async def get_shelf_item_by_id(
            self,
            shelf_item_id: int,
    ) -> ShelfItem:
        result = await self.shelf_item_repo.get_shelf_item_by_id(shelf_item_id=shelf_item_id)
        if not result:
            raise ShelfItemNotFoundError("Shelf item not found")
        return result

    async def get_shelf_by_item(
            self,
            shelf_item_id: int
    ) -> Shelf:
        result = await self.shelf_item_repo.get_shelf_by_item(shelf_item_id=shelf_item_id)
        if not result:
            raise ShelfNotFoundError("Shelf not found")
        return result

