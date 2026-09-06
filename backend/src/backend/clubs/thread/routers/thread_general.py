from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.thread.dependencies import get_thread_manager, get_thread_general_or_404
from src.backend.clubs.thread.managers.thread import ThreadManager
from src.backend.clubs.thread.models import Thread
from src.backend.clubs.thread.schemas import GetThread, CreateThread, UpdateThread
from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User

router = APIRouter(
    prefix="/{club_id}/thread",
)

@cbv(router)
class ThreadGeneralRouter:
    """CBV router for club-general threads: create, update, lock/pin state, delete, and list."""

    manager: ThreadManager = Depends(get_thread_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.post(
        "/",
        summary="creating general thread",
        response_model=GetThread,
        tags=["threads"],
    )
    async def create_thread(
            self,
            request: CreateThread
    ):
        """Creates a new club-general thread."""
        result = await self.manager.creat_general_thread(self.user, self.club, request)
        return result

    @router.put(
        "/{thread_id}",
        summary="update general thread",
        tags=["threads"],
    )
    async def update_thread(
            self,
            request: UpdateThread,
            thread: Thread = Depends(get_thread_general_or_404),
    ):
        """Updates a club-general thread's title."""
        await self.manager.update_thread(self.user, self.club, thread, request)

    @router.put(
        "/{thread_id}/lock",
        summary="locking general thread",
        tags=["threads"],
    )
    async def lock_thread(
            self,
            thread: Thread = Depends(get_thread_general_or_404),
    ):
        """Locks a club-general thread."""
        await self.manager.update_thread_lock(self.user, self.club, thread)

    @router.put(
        "/{thread_id}/unlock",
        summary="unlocking general thread",
        tags=["threads"],
    )
    async def unlock_thread(
            self,
            thread: Thread = Depends(get_thread_general_or_404),
    ):
        """Unlocks a club-general thread."""
        await self.manager.update_thread_unlock(self.user, self.club, thread)

    @router.put(
        "/{thread_id}/pin",
        summary="pining general thread",
        tags=["threads"],
    )
    async def pin_thread(
            self,
            thread: Thread = Depends(get_thread_general_or_404),
    ):
        """Pins a club-general thread."""
        await self.manager.update_thread_pin(self.user, self.club, thread)

    @router.put(
        "/{thread_id}/unpin",
        summary="unpining general thread",
        tags=["threads"],
    )
    async def unpin_thread(
            self,
            thread: Thread = Depends(get_thread_general_or_404),
    ):
        """Unpins a club-general thread."""
        await self.manager.update_thread_unpin(self.user, self.club, thread)

    @router.delete(
        "/{thread_id}",
        summary="deleting general thread",
        tags=["threads"],
    )
    async def delete_thread(
            self,
            thread: Thread = Depends(get_thread_general_or_404)
    ):
        """Deletes a club-general thread."""
        await self.manager.delete_thread(self.user, self.club, thread)

    @router.get(
        "/",
        summary="getting club general threads",
        response_model=list[GetThread],
        tags=["threads"],
    )
    async def get_club_general_threads(
            self,
    ):
        """Lists all club-general threads for the club."""
        result = await self.manager.get_club_general_threads(self.club)
        return result
