from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv

from src.backend.identity.users.dependencies import get_user_or_404
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.library.shelf.dependencies import get_shelf_manager, get_shelf_or_404
from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.library.shelf.models import Shelf
from src.backend.library.shelf.schemas import GetShelf, CreateShelf, UpdateShelf, UpdateShelfVisibility

router = APIRouter(
    prefix="/shelf",
    tags=["shelf"]
)

@cbv(router)
class ShelfRouter:
    shelf_manager: ShelfManager = Depends(get_shelf_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating custom shelf",
        response_model=GetShelf
    )
    async def create_custom_shelf(
            self,
            request: CreateShelf
    ):
        result = await self.shelf_manager.create_custom_shelf(self.user, request)
        return result

    @router.put(
        "/{shelf_id}",
        summary="updating custom shelf",
    )
    async def update_shelf(
            self,
            request: UpdateShelf,
            shelf: Shelf = Depends(get_shelf_or_404),
    ):
        await self.shelf_manager.update_shelf(self.user, shelf, request)

    @router.put(
        "/{shelf_id}/visibility",
        summary="updating shelf visibility",
    )
    async def update_shelf_visibility(
            self,
            request: UpdateShelfVisibility,
            shelf: Shelf = Depends(get_shelf_or_404),
    ):
        await self.shelf_manager.update_shelf_visibility(self.user, shelf, request)

    @router.delete(
        "/{shelf_id}",
        summary="deleting shelf",
    )
    async def delete_shelf(
            self,
            shelf: Shelf = Depends(get_shelf_or_404),
    ):
        await self.shelf_manager.delete_shelf(self.user, shelf)

    @router.get(
        "/my",
        summary="getting current user's reading shelves",
        response_model=list[GetShelf]
    )
    async def get_my_shelves(
            self,
            user: User = Depends(get_current_user),
    ):
        result = await self.shelf_manager.get_my_shelves(user)
        return result

    @router.get(
        "/name",
        summary="getting user's reading shelf by name",
        response_model=GetShelf
    )
    async def get_shelf_by_name(
            self,
            name: str = Query(default=None),
            user: User = Depends(get_current_user),
    ):
        result = await self.shelf_manager.get_shelf_by_name(user, self.user, name)
        return result

    @router.get(
        "/{user_id}",
        summary="getting user's reading shelves",
        response_model=list[GetShelf]
    )
    async def get_user_shelves(
            self,
            user: User = Depends(get_user_or_404),
    ):
        result = await self.shelf_manager.get_user_shelves(user, self.user)
        return result


    @router.get(
        "/{shelf_id}",
        summary="getting shelf by id",
        response_model=GetShelf
    )
    async def get_shelf_by_id(
            self,
            shelf: Shelf = Depends(get_shelf_or_404),
    ):
        return shelf