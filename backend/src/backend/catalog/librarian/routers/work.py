from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models import User
from src.backend.catalog.books.dependencies.work import get_work_manager, get_work_or_404
from src.backend.catalog.books.managers.work import WorkManager
from src.backend.catalog.books.models import Work
from src.backend.catalog.books.schemas.work import CreateWork, UpdateWork, GetWork

from src.backend.catalog.librarian.dependencies import is_librarian

router = APIRouter(
    prefix="/librarian/work",
    tags=["librarian_work"]
)


@cbv(router)
class LibrarianWorkRouter:
    manager: WorkManager = Depends(get_work_manager)
    user: User = Depends(is_librarian)

    @router.post(
        "/",
        summary="creating work",
        response_model=GetWork
    )
    async def create_work(
            self,
            request: CreateWork
    ):
        result = await self.manager.create_work(request)
        return result

    @router.put(
        "/{work_id}",
        summary="updating work",
    )
    async def update_work(
            self,
            request: UpdateWork,
            work: Work = Depends(get_work_or_404)
    ):
        await self.manager.update_work(work.id, request)

    @router.delete(
        "/{work_id}",
        summary="deleting work",
    )
    async def delete_work(
            self,
            work: Work = Depends(get_work_or_404)
    ):
        await self.manager.delete_work(work.id)

