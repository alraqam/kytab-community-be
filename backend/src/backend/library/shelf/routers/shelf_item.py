from fastapi import APIRouter, Depends, Query, status
from fastapi_utils.cbv import cbv

from src.backend.identity.users.dependencies.user import get_user_or_404
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.library.shelf.dependencies.shelf import get_shelf_item_manager, get_shelf_item_or_404, get_shelf_or_404
from src.backend.library.shelf.managers.shelf_item import ShelfItemManager
from src.backend.library.shelf.models.shelf import ShelfItem, Shelf
from src.backend.library.shelf.schemas.shelf import GetShelfItem, CreateShelfItem, UpdateShelfItemEdition
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{shelf_id}/item",
)

@cbv(router)
class ShelfItemRouter:
    """CBV router for managing the items on a shelf: adding, removing, and listing."""

    shelf: Shelf = Depends(get_shelf_or_404)
    shelf_item_manager: ShelfItemManager = Depends(get_shelf_item_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="adding item to shelf",
        response_model=GetShelfItem,
        tags=["shelf_item"],
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404, 409),
    )
    async def add_to_shelf(
            self,
            request: CreateShelfItem
    ):
        """Adds a work to the shelf."""
        result = await self.shelf_item_manager.add_to_shelf(self.user, self.shelf, request)
        return result

    @router.put(
        "/{shelf_item_id}/edition",
        summary="updating shelf item's preferred edition",
        tags=["shelf_item"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def update_edition(
            self,
            request: UpdateShelfItemEdition,
            shelf_item: ShelfItem = Depends(get_shelf_item_or_404),
    ):
        """Sets the shelf item's preferred edition of its work."""
        await self.shelf_item_manager.update_edition(self.user, self.shelf, shelf_item, request)

    @router.delete(
        "/{shelf_item_id}",
        summary="removing item from shelf",
        tags=["shelf_item"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def remove_from_shelf(
            self,
            shelf_item: ShelfItem = Depends(get_shelf_item_or_404),
    ):
        """Removes an item from the shelf."""
        await self.shelf_item_manager.remove_from_shelf(self.user, shelf_item)

    @router.get(
        "/my",
        summary="getting current user's reading shelf items",
        response_model=list[GetShelfItem],
        tags=["shelf_item"],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_my_shelf_items(
            self,
    ):
        """Lists the items on the current user's shelf."""
        result = await self.shelf_item_manager.get_my_shelf_items(self.user, self.shelf)
        return result

    @router.get(
        "/user/{user_id}",
        summary="getting user's shelf items",
        response_model=list[GetShelfItem],
        tags=["shelf_item"],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_user_shelf_items(
            self,
            user: User = Depends(get_user_or_404),
    ):
        """Lists the items on another user's shelf, if visible to the current user."""
        result = await self.shelf_item_manager.get_user_shelf_items(user, self.user, self.shelf)
        return result

    @router.get(
        "/{shelf_item_id}",
        summary="getting shelf item by id",
        response_model=GetShelfItem,
        tags=["shelf_item"],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_shelf_item_by_id(
            self,
            shelf_item_id: int
    ):
        """Fetches a single shelf item by ID."""
        result = await self.shelf_item_manager.get_shelf_item_by_id(shelf_item_id)
        return result