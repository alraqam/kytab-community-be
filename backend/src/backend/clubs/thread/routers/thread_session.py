from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.clubs.reading_session.dependencies.reading_session import get_reading_session_or_404, get_milestone_or_404
from src.backend.clubs.reading_session.models.reading_session import ReadingSession, Milestone
from src.backend.clubs.thread.dependencies.thread import get_thread_manager, get_thread_session_or_404
from src.backend.clubs.thread.managers.thread import ThreadManager
from src.backend.clubs.thread.models.thread import Thread
from src.backend.clubs.thread.schemas.thread import GetThread, CreateThread, UpdateThread
from src.backend.clubs.clubs.dependencies.club import get_club_or_404
from src.backend.clubs.clubs.models.club import Club
from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/{milestone_id}/thread",
)

@cbv(router)
class ThreadSessionRouter:
    """CBV router for threads scoped to a reading-session milestone: create, update, lock/pin state, delete, and milestone-gated listing."""

    manager: ThreadManager = Depends(get_thread_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)
    reading_session: ReadingSession = Depends(get_reading_session_or_404)
    milestone: Milestone = Depends(get_milestone_or_404)

    @router.post(
        "/",
        summary="creating milestone thread",
        response_model=GetThread,
        tags=["threads"],
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 403, 404),
    )
    async def create_thread(
            self,
            request: CreateThread
    ):
        """Creates a new thread scoped to the session milestone."""
        result = await self.manager.create_milestone_thread(self.user, self.club, self.reading_session, self.milestone, request)
        return result

    @router.put(
        "/{thread_id}",
        summary="update milestone thread",
        tags=["threads"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def update_thread(
            self,
            request: UpdateThread,
            thread: Thread = Depends(get_thread_session_or_404),
    ):
        """Updates a milestone thread's title."""
        await self.manager.update_thread(self.user, self.club, thread, request)

    @router.put(
        "/{thread_id}/lock",
        summary="locking milestone thread",
        tags=["threads"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def lock_thread(
            self,
            thread: Thread = Depends(get_thread_session_or_404),
    ):
        """Locks a milestone thread."""
        await self.manager.update_thread_lock(self.user, self.club, thread)

    @router.put(
        "/{thread_id}/unlock",
        summary="unlocking milestone thread",
        tags=["threads"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def unlock_thread(
            self,
            thread: Thread = Depends(get_thread_session_or_404),
    ):
        """Unlocks a milestone thread."""
        await self.manager.update_thread_unlock(self.user, self.club, thread)

    @router.put(
        "/{thread_id}/pin",
        summary="pining milestone thread",
        tags=["threads"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def pin_thread(
            self,
            thread: Thread = Depends(get_thread_session_or_404),
    ):
        """Pins a milestone thread."""
        await self.manager.update_thread_pin(self.user, self.club, thread)

    @router.put(
        "/{thread_id}/unpin",
        summary="unpining milestone thread",
        tags=["threads"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404, 409),
    )
    async def unpin_thread(
            self,
            thread: Thread = Depends(get_thread_session_or_404),
    ):
        """Unpins a milestone thread."""
        await self.manager.update_thread_unpin(self.user, self.club, thread)

    @router.delete(
        "/{thread_id}",
        summary="deleting milestone thread",
        tags=["threads"],
        status_code=status.HTTP_204_NO_CONTENT,
        responses=error_responses(401, 403, 404),
    )
    async def delete_thread(
            self,
            thread: Thread = Depends(get_thread_session_or_404)
    ):
        """Deletes a milestone thread."""
        await self.manager.delete_thread(self.user, self.club, thread)

    @router.get(
        "/",
        summary="getting club milestone threads by user milestone reached",
        response_model=list[GetThread],
        tags=["threads"],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def get_session_milestone_threads(
            self,
    ):
        """Lists milestone threads visible based on the user's reading progress."""
        result = await self.manager.get_session_milestone_threads(self.user, self.club, self.reading_session, self.milestone)
        return result

    @router.get(
        "/{thread_id}/reveal",
        summary="getting and revealing thread by id",
        response_model=GetThread,
        tags=["threads"],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 403, 404),
    )
    async def reveal_thread(
            self,
            thread: Thread = Depends(get_thread_session_or_404),
    ):
        """Fetches and reveals a single milestone thread by ID, regardless of the user's milestone progress."""
        return await self.manager.reveal_thread(self.user, self.club, thread)
