from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from backend.identity.auth.dependencies import get_current_user
from backend.identity.auth.models import User
from backend.library.progress.dependencies import get_reading_period_manager, get_reading_period_or_404
from backend.library.progress.managers.reading_period import ReadingPeriodManager
from backend.library.progress.models import ReadingPeriod
from backend.library.progress.schemas import GetReadingPeriod
from backend.library.shelf.dependencies import get_shelf_item_or_404
from backend.library.shelf.models import ShelfItem

router = APIRouter(
    prefix="/{shelf_item_id}/period",
    tags=["reading_period"],
)

@cbv(router)
class ReadingPeriodRouter:
    shelf_item: ShelfItem = Depends(get_shelf_item_or_404)
    period_manager: ReadingPeriodManager = Depends(get_reading_period_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="start reading period",
        response_model=GetReadingPeriod
    )
    async def create_custom_shelf(
            self,
    ):
        result = await self.period_manager.start_reading_period(self.user, self.shelf_item)
        return result

    @router.put(
        "/{reading_period_id}",
        summary="set finished reading period",
    )
    async def set_finishing_date(
            self,
            reading_period: ReadingPeriod = Depends(get_reading_period_or_404)
    ):
        await self.period_manager.set_finishing_date(self.user, reading_period)

    @router.delete(
        "/{reading_period_id}",
        summary="deleting reading period",
    )
    async def delete_reading_period(
            self,
            reading_period: ReadingPeriod = Depends(get_reading_period_or_404)
    ):
        await self.period_manager.delete_reading_period(self.user, reading_period)

    @router.post(
        "/",
        summary="getting shelf item's reading periods",
        response_model=list[GetReadingPeriod]
    )
    async def get_shelf_item_periods(
            self,
    ):
        result = await self.period_manager.get_shelf_item_periods(self.shelf_item)
        return result

    @router.post(
        "/{reading_period_id}",
        summary="getting reading period by id",
        response_model=list[GetReadingPeriod]
    )
    async def get_reading_period_by_id(
            self,
            reading_period: ReadingPeriod = Depends(get_reading_period_or_404)
    ):
        return reading_period