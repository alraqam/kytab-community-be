from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv

from backend.identity.users.dependencies import get_user_or_404
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.library.shelf.dependencies import get_shelf_item_manager, get_shelf_item_or_404, get_shelf_or_404
from src.backend.library.shelf.managers.shelf_item import ShelfItemManager
from src.backend.library.shelf.models import ShelfItem, Shelf
from src.backend.library.shelf.schemas import GetShelfItem, CreateShelfItem

router = APIRouter(
    prefix="/{shelf_id}/item",
    tags=["shelf_item-item"]
)

@cbv(router)
class ShelfItemRouter:
    shelf: Shelf = Depends(get_shelf_or_404)
    shelf_item_manager: ShelfItemManager = Depends(get_shelf_item_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="adding item to shelf",
        response_model=GetShelfItem
    )
    async def add_to_shelf(
            self,
            request: CreateShelfItem
    ):
        result = await self.shelf_item_manager.add_to_shelf(self.user, self.shelf, request)
        return result

    @router.delete(
        "/{shelf_item_id}",
        summary="removing item from shelf",
    )
    async def remove_from_shelf(
            self,
            shelf_item: ShelfItem = Depends(get_shelf_item_or_404),
    ):
        await self.shelf_item_manager.remove_from_shelf(self.user, shelf_item)

    @router.get(
        "/{user_id}",
        summary="getting user's shelf items",
        response_model=list[GetShelfItem]
    )
    async def get_shelf_items(
            self,
            user: User = Depends(get_user_or_404),
    ):
        result = await self.shelf_item_manager.get_shelf_items(user, self.user, self.shelf)
        return result

    @router.get(
        "/my",
        summary="getting current user's reading shelf items",
        response_model=list[GetShelfItem]
    )
    async def get_my_shelf_items(
            self,
    ):
        result = await self.shelf_item_manager.get_my_shelf_items(self.user, self.shelf)
        return result

    @router.get(
        "/{shelf_item_id}",
        summary="getting shelf item by id",
        response_model=GetShelfItem
    )
    async def get_shelf_item_by_id(
            self,
            shelf_item_id: int
    ):
        result = await self.shelf_item_manager.get_shelf_item_by_id(shelf_item_id)
        return result