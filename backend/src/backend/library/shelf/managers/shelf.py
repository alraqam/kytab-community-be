from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.follow.repository import FollowRepository
from src.backend.library.shelf.permissions import is_shelf_owner
from src.backend.library.shelf.exceptions import ShelfAlreadyExistsError, DefaultShelfError, ShelfNotFoundError, \
    PrivateShelfError
from src.backend.library.shelf.models import Shelf
from src.backend.library.shelf.repositories.shelf import ShelfRepository
from src.backend.library.shelf.schemas import CreateShelf, ShelfDefault, ShelfVisibility, UpdateShelf, \
    UpdateShelfVisibility


class ShelfManager:
    """Handles shelf business logic: creation, updates, visibility, and access control."""

    def __init__(
            self,
            session: AsyncSession
    ):

        self.session = session
        self.shelf_repo = ShelfRepository(session)
        self.follow_repo = FollowRepository(session)

    async def ensure_shelf_access(
            self,
            shelf: Shelf,
            current_user: User,
            user: User
    ) -> None:
        """Verifies that the current user is allowed to view the given shelf.

        Args:
            shelf: Shelf being accessed.
            current_user: User requesting access.
            user: Owner of the shelf.

        Raises:
            PrivateShelfError: When the shelf is private and the current user is not
                the owner, or the shelf is followers-only and the current user does
                not follow the owner.
        """
        is_owner = True if current_user.id == user.id else False

        if shelf.visibility == ShelfVisibility.private and not is_owner:
            raise PrivateShelfError("Shelf is private")

        if shelf.visibility == ShelfVisibility.followers_only and not is_owner:
            is_follower = await self.follow_repo.is_following_user(current_user.id, user.id)
            if not is_follower:
                raise PrivateShelfError("Shelf is followers only")

    async def create_default_shelves(
            self,
            user: User,
    ) -> None:
        """Creates the standard set of default shelves for a newly registered user.

        Args:
            user: User for whom the default shelves are created.
        """
        for name in ShelfDefault:
            await self.shelf_repo.create_shelf(
                user_id=user.id,
                name=name,
                is_default=True,
                visibility=ShelfVisibility.public
            )
        await self.session.commit()

    async def create_custom_shelf(
            self,
            user: User,
            request: CreateShelf
    ) -> Shelf:
        """Creates a custom, non-default shelf for the user.

        Args:
            user: User creating the shelf.
            request: CreateShelf payload with the shelf name.

        Returns:
            Newly created Shelf instance.

        Raises:
            ShelfAlreadyExistsError: When the user already has a shelf with this name.
        """
        if await self.shelf_repo.get_shelf_by_name(user.id, request.name):
            raise ShelfAlreadyExistsError("Shelf with this name already exists")

        result = await self.shelf_repo.create_shelf(
            user_id=user.id,
            name=request.name,
            is_default=False,
            visibility=ShelfVisibility.public
        )
        await self.session.commit()
        return await self.shelf_repo.get_shelf_by_id(result.id)

    async def update_shelf(
            self,
            user: User,
            shelf: Shelf,
            request: UpdateShelf
    ) -> None:
        """Renames a non-default shelf.

        Args:
            user: User requesting the update.
            shelf: Shelf to rename.
            request: UpdateShelf payload with the new name.

        Raises:
            IsNotShelfOwnerError: When the user does not own the shelf.
            DefaultShelfError: When the shelf is a default shelf.
        """
        await is_shelf_owner(user, shelf)
        if shelf.is_default:
            raise DefaultShelfError("Default shelves can not be changed")

        await self.shelf_repo.update_shelf(
            shelf=shelf,
            name=request.name
        )
        await self.session.commit()

    async def update_shelf_visibility(
            self,
            user: User,
            shelf: Shelf,
            request: UpdateShelfVisibility
    ) -> None:
        """Updates a shelf's visibility setting.

        Args:
            user: User requesting the update.
            shelf: Shelf whose visibility is being changed.
            request: UpdateShelfVisibility payload with the new visibility.

        Raises:
            IsNotShelfOwnerError: When the user does not own the shelf.
        """
        await is_shelf_owner(user, shelf)
        await self.shelf_repo.update_shelf_visibility(
            shelf=shelf,
            visibility=request.visibility
        )
        await self.session.commit()

    async def delete_shelf(
            self,
            user: User,
            shelf: Shelf,
    ) -> None:
        """Permanently deletes a non-default shelf.

        Args:
            user: User requesting the deletion.
            shelf: Shelf to delete.

        Raises:
            IsNotShelfOwnerError: When the user does not own the shelf.
            DefaultShelfError: When the shelf is a default shelf.
        """
        await is_shelf_owner(user, shelf)
        if shelf.is_default:
            raise DefaultShelfError("Default shelves can not be changed")

        await self.shelf_repo.delete_shelf(
            shelf=shelf,
        )
        await self.session.commit()

    async def get_user_shelves(
            self,
            user: User,
            current_user: User
    ) -> list[Shelf]:
        """Lists a user's shelves that are visible to the current user.

        Shelves the current user is not permitted to view are silently skipped.

        Args:
            user: Owner of the shelves to list.
            current_user: User requesting the list.

        Returns:
            List of Shelf instances the current user may view.
        """
        shelves = await self.shelf_repo.get_user_shelves(user.id)
        result = []
        for shelf in shelves:
            try:
                await self.ensure_shelf_access(shelf, current_user, user)
                result.append(shelf)
            except PrivateShelfError:
                continue
        return result

    async def get_my_shelves(
            self,
            user: User,
    ) -> list[Shelf]:
        """Lists all shelves owned by the given user.

        Args:
            user: User whose shelves are being listed.

        Returns:
            List of the user's Shelf instances.
        """
        shelves = await self.shelf_repo.get_user_shelves(user.id)
        return shelves

    async def get_shelf_by_id(
            self,
            shelf_id: int,
    ) -> Shelf:
        """Fetches a single shelf by ID.

        Args:
            shelf_id: ID of the shelf to fetch.

        Returns:
            Matching Shelf instance.

        Raises:
            ShelfNotFoundError: When no shelf matches the ID.
        """
        result = await self.shelf_repo.get_shelf_by_id(shelf_id=shelf_id)
        if not result:
            raise ShelfNotFoundError("Shelf not found")
        return result

    async def get_shelf_by_name(
            self,
            user: User,
            name: str
    ) -> Shelf:
        """Fetches a user's shelf by name.

        Args:
            user: Owner of the shelf.
            name: Name of the shelf to fetch.

        Returns:
            Matching Shelf instance.

        Raises:
            ShelfNotFoundError: When the user has no shelf with this name.
        """
        shelf = await self.shelf_repo.get_shelf_by_name(user.id, name)
        if not shelf:
            raise ShelfNotFoundError("Shelf not found")
        return shelf