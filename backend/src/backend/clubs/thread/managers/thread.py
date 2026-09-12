from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.managers.milestone import MilestoneManager
from src.backend.clubs.reading_session.managers.progress import MilestoneProgressManager
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.core.storage import StorageService
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.thread.exceptions import LockedThreadError, PinnedThreadError, ThreadNotFoundError, \
    MilestoneNotReachedError
from src.backend.clubs.thread.models import Thread
from src.backend.clubs.thread.repository.thread import ThreadRepository
from src.backend.clubs.thread.schemas import CreateThread, UpdateThread
from src.backend.identity.auth.models import User


class ThreadManager:
    """Handles business logic for discussion threads: creation, updates, lock/pin state, deletion, and milestone-gated retrieval."""

    def __init__(
            self,
            session: AsyncSession
    ):
        """Initializes the manager and its dependent repositories and managers.

        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session
        self.thread_repo = ThreadRepository(session)
        self.club_manager = ClubManager(session, StorageService())
        self.milestone_progress_manager = MilestoneProgressManager(session)
        self.milestone_manager = MilestoneManager(session)

    async def create_milestone_thread(
            self,
            user: User,
            club: Club,
            reading_session: ReadingSession,
            milestone: Milestone,
            request: CreateThread
    ) -> Thread:
        """Creates a new thread scoped to a reading session milestone.

        Args:
            user: User creating the thread; must be a club owner or moderator.
            club: Club the thread belongs to.
            reading_session: Reading session the milestone belongs to.
            milestone: Milestone the thread is scoped to.
            request: CreateThread payload with the thread title.

        Returns:
            Newly created Thread instance.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
        """
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
        return await self.thread_repo.get_thread_by_id(response.id)

    async def creat_general_thread(
            self,
            user: User,
            club: Club,
            request: CreateThread
    ) -> Thread:
        """Creates a new club-general thread, not scoped to any reading session.

        Args:
            user: User creating the thread; must be a club owner or moderator.
            club: Club the thread belongs to.
            request: CreateThread payload with the thread title.

        Returns:
            Newly created Thread instance.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
        """
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
        return await self.thread_repo.get_thread_by_id(response.id)

    async def update_thread(
            self,
            user: User,
            club: Club,
            thread: Thread,
            request: UpdateThread
    ) -> None:
        """Updates a thread's title.

        Args:
            user: User requesting the update; must be a club owner or moderator.
            club: Club the thread belongs to.
            thread: Thread instance to update.
            request: UpdateThread payload with the new title.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
            LockedThreadError: When the thread is locked.
        """
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
        """Locks a thread, preventing further posts and edits.

        Args:
            user: User requesting the lock; must be a club owner or moderator.
            club: Club the thread belongs to.
            thread: Thread instance to lock.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
            LockedThreadError: When the thread is already locked.
        """
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
        """Unlocks a previously locked thread.

        Args:
            user: User requesting the unlock; must be a club owner or moderator.
            club: Club the thread belongs to.
            thread: Thread instance to unlock.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
            LockedThreadError: When the thread is not locked.
        """
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
        """Pins a thread.

        Args:
            user: User requesting the pin; must be a club owner or moderator.
            club: Club the thread belongs to.
            thread: Thread instance to pin.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
            PinnedThreadError: When the thread is already pinned.
        """
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
        """Unpins a previously pinned thread.

        Args:
            user: User requesting the unpin; must be a club owner or moderator.
            club: Club the thread belongs to.
            thread: Thread instance to unpin.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
            LockedThreadError: When the thread is not pinned.
        """
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
        """Deletes a thread.

        Args:
            user: User requesting the deletion; must be a club owner or moderator.
            club: Club the thread belongs to.
            thread: Thread instance to delete.

        Raises:
            IsNotClubOwnerError: When the user is not a club owner or moderator.
        """
        is_owner_or_moderator(club, user.id)

        await self.thread_repo.delete_thread(
            thread=thread,
        )
        await self.session.commit()

    async def get_club_general_threads(
            self,
            club: Club
    ) -> list[Thread]:
        """Lists all club-general threads for a club, pinned threads first.

        Args:
            club: Club to list threads for.

        Returns:
            List of Thread instances.
        """
        threads = await self.thread_repo.get_club_general_threads(
            club_id=club.id,
        )
        return threads

    async def get_all_session_milestone_threads(
            self,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> list[Thread]:
        """Lists all threads scoped to a session milestone, without progress gating.

        Args:
            reading_session: Reading session the milestone belongs to.
            milestone: Milestone to list threads for.

        Returns:
            List of Thread instances.
        """
        threads = await self.thread_repo.get_session_milestone_threads(
            session_id=reading_session.id,
            milestone_id=milestone.id,
        )
        return threads

    async def get_session_milestone_threads(
            self,
            user: User,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> list[Thread]:
        """Lists threads scoped to a session milestone, gated by the user's reading progress.

        Args:
            user: User requesting the threads.
            reading_session: Reading session the milestone belongs to.
            milestone: Milestone to list threads for.

        Returns:
            List of Thread instances.

        Raises:
            MilestoneNotReachedError: When the user has no recorded progress, or has not
                yet reached the given milestone.
        """
        threads = await self.thread_repo.get_session_milestone_threads(
            session_id=reading_session.id,
            milestone_id=milestone.id,
        )

        progress = await self.milestone_progress_manager.get_user_milestone_progress(reading_session, user)
        if not progress:
            raise MilestoneNotReachedError("Milestone for this thread not reached")

        if progress.is_finished:
            return threads

        index_reached = await self.milestone_manager.get_milestone_by_id(milestone_id=progress.milestone_id)
        if milestone.order_index > index_reached.order_index:
            raise MilestoneNotReachedError("Milestone for this thread not reached")

        return threads

    async def get_thread_by_id(
            self,
            thread_id: int,
    ) -> Thread:
        """Fetches a thread by ID.

        Args:
            thread_id: ID of the thread to fetch.

        Returns:
            Matching Thread instance.

        Raises:
            ThreadNotFoundError: When no thread with the given ID exists.
        """
        thread = await self.thread_repo.get_thread_by_id(
            thread_id=thread_id,
        )
        if not thread:
            raise ThreadNotFoundError("Thread not found")
        return thread
