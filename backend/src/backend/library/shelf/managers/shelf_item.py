from sqlalchemy.ext.asyncio import AsyncSession

from backend.library.shelf.exceptions import IsNotShelfOwnerError
from src.backend.identity.auth.models import User
from src.backend.identity.follow.repository import FollowRepository
from src.backend.library.shelf.dependencies import is_shelf_owner
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
        self.follow_repo = FollowRepository(session)

    async def add_to_shelf(
            self,
            user: User,
            shelf: Shelf,
            request: CreateShelfItem
    ) -> ShelfItem:
        await is_shelf_owner(user, shelf)

        result = await self.shelf_item_repo.add_to_shelf(
            shelf_id=shelf.id,
            work_id=request.work_id,
            edition_id=request.edition_id
        )
        await self.session.commit()
        return result

    async def remove_from_shelf(
            self,
            user: User,
            shelf_item: ShelfItem,
    ) -> None:
        shelf = await self.shelf_item_repo.get_shelf_by_item(shelf_item.id)
        await is_shelf_owner(user, shelf)

        result = await self.shelf_item_repo.remove_from_shelf(
            shelf_item=shelf_item
        )
        await self.session.commit()
        return result

    async def get_shelf_items(
            self,
            user: User,
            current_user: User,
            shelf: Shelf
    ) -> list[ShelfItem]:
        items = await self.shelf_item_repo.get_shelf_items(shelf.id)

        if shelf.user_id == current_user.id:
            return items

        if shelf.visibility == ShelfVisibility.private:
            raise PrivateShelfError("Shelf is private")

        if shelf.visibility == ShelfVisibility.followers_only:
            is_follower = True if await self.follow_repo.is_following_user(current_user.id, user.id) else False
            if not is_follower:
                raise PrivateShelfError("Shelf is followers only")

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

