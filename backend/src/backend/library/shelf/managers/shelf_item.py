from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.catalog.books.exceptions import InvalidWorkEditionError
from src.backend.catalog.books.managers.edition import EditionManager
from src.backend.catalog.books.managers.work import WorkManager
from src.backend.identity.follow.managers import FollowManager
from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.exceptions import IsNotShelfOwnerError, ShelfNotFoundError, WorkAlreadyInShelfError
from src.backend.identity.auth.models import User
from src.backend.library.shelf.permissions import is_shelf_owner
from src.backend.library.shelf.exceptions import PrivateShelfError, ShelfItemNotFoundError
from src.backend.library.shelf.models import Shelf, ShelfItem
from src.backend.library.shelf.repositories.shelf_item import ShelfItemRepository
from src.backend.library.shelf.schemas import CreateShelfItem, ShelfVisibility, UpdateShelfItemEdition


class ShelfItemManager:
    """Handles shelf item business logic: adding, removing, and moving works between shelves."""

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
        """Adds a work, and optionally a specific edition, to a shelf.

        Args:
            user: User adding the item.
            shelf: Shelf the item is being added to.
            request: CreateShelfItem payload with the work and optional edition IDs.

        Returns:
            Newly created ShelfItem instance.

        Raises:
            IsNotShelfOwnerError: When the user does not own the shelf.
            WorkNotFoundError: When the given work does not exist.
            EditionNotFoundError: When the given edition does not exist.
            InvalidWorkEditionError: When the given edition does not belong to the given work.
            WorkAlreadyInShelfError: When the work is already present in one of the user's shelves.
        """
        await is_shelf_owner(user, shelf)

        work = await self.work_manager.get_work_by_id(request.work_id)
        edition = await self.edition_manager.get_edition_by_id(request.edition_id) if request.edition_id else None

        if edition and edition.work_id != work.id:
            raise InvalidWorkEditionError("Invalid work edition")

        exists = await self.shelf_item_repo.exists_in_shelf(user.id, request.work_id)
        if exists:
            raise WorkAlreadyInShelfError("Work is already added to shelf")

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
        """Removes an item from its shelf.

        Args:
            user: User requesting the removal.
            shelf_item: ShelfItem to remove.

        Raises:
            ShelfNotFoundError: When the shelf item has no associated shelf.
            IsNotShelfOwnerError: When the user does not own the shelf.
        """
        shelf = await self.shelf_item_repo.get_shelf_by_item(shelf_item.id)
        if not shelf:
            raise ShelfNotFoundError("Shelf not found")

        await is_shelf_owner(user, shelf)

        result = await self.shelf_item_repo.remove_from_shelf(
            shelf_item=shelf_item
        )
        await self.session.commit()
        return result

    async def update_edition(
            self,
            user: User,
            shelf: Shelf,
            shelf_item: ShelfItem,
            request: UpdateShelfItemEdition
    ) -> None:
        """Sets a shelf item's preferred edition of its work.

        Args:
            user: User requesting the update.
            shelf: Shelf that owns the shelf item.
            shelf_item: ShelfItem whose preferred edition is being set.
            request: UpdateShelfItemEdition payload with the new edition ID.

        Raises:
            IsNotShelfOwnerError: When the user does not own the shelf.
            EditionNotFoundError: When the given edition does not exist.
            InvalidWorkEditionError: When the given edition does not belong to the
                shelf item's work.
        """
        await is_shelf_owner(user, shelf)

        edition = await self.edition_manager.get_edition_by_id(request.edition_id) if request.edition_id else None
        if edition and edition.work_id != shelf_item.work_id:
            raise InvalidWorkEditionError("Invalid work edition")

        await self.shelf_item_repo.update_edition(
            shelf_item=shelf_item,
            edition_id=edition.id if edition else None,
        )
        await self.session.commit()

    async def change_shelf(
            self,
            user: User,
            shelf_item: ShelfItem,
            shelf: Shelf
    ) -> None:
        """Moves a shelf item to a different shelf.

        Args:
            user: User requesting the move.
            shelf_item: ShelfItem to move.
            shelf: Destination shelf.

        Raises:
            IsNotShelfOwnerError: When the user does not own the destination shelf.
        """
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
        """Lists a shelf's items after verifying the current user can view the shelf.

        Args:
            user: Owner of the shelf.
            current_user: User requesting the items.
            shelf: Shelf whose items are being listed.

        Returns:
            List of ShelfItem instances on the shelf.

        Raises:
            PrivateShelfError: When the shelf's visibility does not permit the current
                user to view it.
        """
        await self.shelf_manager.ensure_shelf_access(shelf, current_user, user)
        items = await self.shelf_item_repo.get_shelf_items(shelf.id)
        return items

    async def get_my_shelf_items(
            self,
            user: User,
            shelf: Shelf
    ) -> list[ShelfItem]:
        """Lists the items on a shelf owned by the given user.

        Args:
            user: User requesting the items, expected to own the shelf.
            shelf: Shelf whose items are being listed.

        Returns:
            List of ShelfItem instances on the shelf.

        Raises:
            IsNotShelfOwnerError: When the user does not own the shelf.
        """
        if user.id != shelf.user_id:
            raise IsNotShelfOwnerError("Is not shelf owner")
        items = await self.shelf_item_repo.get_shelf_items(shelf.id)
        return items

    async def get_shelf_item_by_id(
            self,
            shelf_item_id: int,
    ) -> ShelfItem:
        """Fetches a single shelf item by ID.

        Args:
            shelf_item_id: ID of the shelf item to fetch.

        Returns:
            Matching ShelfItem instance.

        Raises:
            ShelfItemNotFoundError: When no shelf item matches the ID.
        """
        result = await self.shelf_item_repo.get_shelf_item_by_id(shelf_item_id=shelf_item_id)
        if not result:
            raise ShelfItemNotFoundError("Shelf item not found")
        return result

    async def get_shelf_by_item(
            self,
            shelf_item_id: int
    ) -> Shelf:
        """Fetches the shelf that contains the given shelf item.

        Args:
            shelf_item_id: ID of the shelf item whose shelf is being fetched.

        Returns:
            Matching Shelf instance.

        Raises:
            ShelfNotFoundError: When no shelf contains a shelf item with this ID.
        """
        result = await self.shelf_item_repo.get_shelf_by_item(shelf_item_id=shelf_item_id)
        if not result:
            raise ShelfNotFoundError("Shelf not found")
        return result

