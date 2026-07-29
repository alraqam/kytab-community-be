from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.thread.exceptions import LockedThreadError, PinnedThreadError, ThreadNotFoundError
from src.backend.clubs.thread.models import Thread
from src.backend.clubs.thread.repository.thread import ThreadRepository
from src.backend.clubs.thread.schemas import CreateThread, UpdateThread
from src.backend.identity.auth.models import User


class ThreadManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.thread_repo = ThreadRepository(session)
        self.club_manager = ClubManager(session)

    async def create_milestone_thread(
            self,
            user: User,
            club: Club,
            reading_session: ReadingSession,
            milestone: Milestone,
            request: CreateThread
    ) -> Thread:
        is_owner_or_moderator(club, user.id)

        response = await self.thread_repo.create_thread(
            club_id=club.id,
            is_general=False,
            title=request.title,
            created_by_id=user.id,
            session_id=reading_session.id,
            milestone_id=milestone.id,
        )
        await self.session.commit()
        return response

    async def creat_general_thread(
            self,
            user: User,
            club: Club,
            request: CreateThread
    ) -> Thread:
        is_owner_or_moderator(club, user.id)

        response = await self.thread_repo.create_thread(
            club_id=club.id,
            is_general=True,
            title=request.title,
            created_by_id=user.id,
            session_id=None,
            milestone_id=None,
        )
        await self.session.commit()
        return response

    async def update_thread(
            self,
            user: User,
            club: Club,
            thread: Thread,
            request: UpdateThread
    ) -> None:
        is_owner_or_moderator(club, user.id)

        if thread.is_locked:
            raise LockedThreadError("Thread is locked")

        await self.thread_repo.update_thread(
            thread=thread,
            title=request.title,
        )
        await self.session.commit()

    async def update_thread_lock(
            self,
            user: User,
            club: Club,
            thread: Thread,
    ) -> None:
        is_owner_or_moderator(club, user.id)

        if thread.is_locked:
            raise LockedThreadError("Thread is locked")

        await self.thread_repo.update_thread_lock(
            thread=thread,
            status=True
        )
        await self.session.commit()

    async def update_thread_unlock(
            self,
            user: User,
            club: Club,
            thread: Thread,
    ) -> None:
        is_owner_or_moderator(club, user.id)

        if not thread.is_locked:
            raise LockedThreadError("Thread is not locked")

        await self.thread_repo.update_thread_lock(
            thread=thread,
            status=False
        )
        await self.session.commit()

    async def update_thread_pin(
            self,
            user: User,
            club: Club,
            thread: Thread,
    ) -> None:
        is_owner_or_moderator(club, user.id)

        if thread.is_pinned:
            raise PinnedThreadError("Thread is pined")

        await self.thread_repo.update_thread_pin(
            thread=thread,
            status=True
        )
        await self.session.commit()

    async def update_thread_unpin(
            self,
            user: User,
            club: Club,
            thread: Thread,
    ) -> None:
        is_owner_or_moderator(club, user.id)

        if not thread.is_pinned:
            raise LockedThreadError("Thread is not pined")

        await self.thread_repo.update_thread_pin(
            thread=thread,
            status=False
        )
        await self.session.commit()

    async def delete_thread(
            self,
            user: User,
            club: Club,
            thread: Thread,
    ) -> None:
        is_owner_or_moderator(club, user.id)

        await self.thread_repo.delete_thread(
            thread=thread,
        )
        await self.session.commit()

    async def get_session_milestone_threads(
            self,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> list[Thread]:
        threads = await self.thread_repo.get_session_milestone_threads(
            session_id=reading_session.id,
            milestone_id=milestone.id,
        )
        return threads

    async def get_club_general_threads(
            self,
            club: Club
    ) -> list[Thread]:
        threads = await self.thread_repo.get_club_general_threads(
            club_id=club.id,
        )
        return threads

    async def get_thread_by_id(
            self,
            thread_id: int,
    ) -> Thread:
        thread = await self.thread_repo.get_thread_by_id(
            thread_id=thread_id,
        )
        if not thread:
            raise ThreadNotFoundError("Thread not found")
        return thread