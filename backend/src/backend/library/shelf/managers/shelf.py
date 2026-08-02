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
        if await self.shelf_repo.get_shelf_by_name(user.id, request.name):
            raise ShelfAlreadyExistsError("Shelf with this name already exists")

        result = await self.shelf_repo.create_shelf(
            user_id=user.id,
            name=request.name,
            is_default=False,
            visibility=ShelfVisibility.public
        )
        await self.session.commit()
        return result

    async def update_shelf(
            self,
            user: User,
            shelf: Shelf,
            request: UpdateShelf
    ) -> None:
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
        shelves = await self.shelf_repo.get_user_shelves(user.id)
        return shelves

    async def get_shelf_by_id(
            self,
            shelf_id: int,
    ) -> Shelf:
        result = await self.shelf_repo.get_shelf_by_id(shelf_id=shelf_id)
        if not result:
            raise ShelfNotFoundError("Shelf not found")
        return result

    async def get_shelf_by_name(
            self,
            user: User,
            name: str
    ) -> Shelf:
        shelf = await self.shelf_repo.get_shelf_by_name(user.id, name)
        if not shelf:
            raise ShelfNotFoundError("Shelf not found")
        return shelf