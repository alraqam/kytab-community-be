from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models import User
from src.backend.catalog.books.dependencies.work import get_work_manager, get_work_or_404
from src.backend.catalog.books.managers.work import WorkManager
from src.backend.catalog.books.models import Work
from src.backend.catalog.books.schemas.work import CreateWork, UpdateWork, GetWork, MergeWork

from src.backend.catalog.librarian.dependencies import is_librarian

router = APIRouter(
    prefix="/librarian/work",
    tags=["librarian_work"]
)


@cbv(router)
class LibrarianWorkRouter:
    """CBV router for librarian management of works: create, update, delete, and merge duplicates."""

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
        """Creates a new work."""
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
        """Updates an existing work's details."""
        await self.manager.update_work(work.id, request)

    @router.delete(
        "/{work_id}",
        summary="deleting work",
    )
    async def delete_work(
            self,
            work: Work = Depends(get_work_or_404)
    ):
        """Deletes a work."""
        await self.manager.delete_work(work.id)

    @router.put(
        "/{work_id}/merge",
        summary="merging duplicate work into this work",
        response_model=GetWork,
    )
    async def merge_work(
            self,
            request: MergeWork,
            work: Work = Depends(get_work_or_404)
    ):
        """Merges a duplicate work into this work."""
        result = await self.manager.merge_works(request.source_work_id, work.id)
        return result

