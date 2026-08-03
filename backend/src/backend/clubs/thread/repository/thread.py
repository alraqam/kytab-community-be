from dataclasses import dataclass

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.models import Thread


@dataclass
class ThreadRepository:
    """Data-access layer for thread persistence and queries."""

    session: AsyncSession

    async def create_thread(
            self,
            club_id: int,
            is_general: bool,
            title: str,
            created_by_id: int,
            session_id: int | None = None,
            milestone_id: int | None = None,
    ) -> Thread:
        """Inserts a new thread, unlocked and unpinned by default.

        Args:
            club_id: ID of the club the thread belongs to.
            is_general: Whether the thread is a club-general thread.
            title: Thread title.
            created_by_id: ID of the user creating the thread.
            session_id: ID of the reading session the thread is scoped to, or None for a general thread.
            milestone_id: ID of the milestone the thread is scoped to, or None for a general thread.

        Returns:
            Newly created Thread instance.
        """
        result = Thread(
            club_id=club_id,
            is_general=is_general,
            title=title,
            created_by_id=created_by_id,
            is_locked=False,
            is_pinned=False,
            session_id=session_id,
            milestone_id=milestone_id,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_thread(
            self,
            thread: Thread,
            title: str
    ) -> None:
        """Updates a thread's title.

        Args:
            thread: Thread instance to update.
            title: New title.
        """
        thread.title = title
        self.session.add(thread)
        await self.session.flush()

    async def update_thread_lock(
            self,
            thread: Thread,
            status: bool,
    ) -> None:
        """Sets a thread's locked flag.

        Args:
            thread: Thread instance to update.
            status: True to lock the thread, False to unlock it.
        """
        thread.is_locked = status
        self.session.add(thread)
        await self.session.flush()

    async def update_thread_pin(
            self,
            thread: Thread,
            status: bool,
    ) -> None:
        """Sets a thread's pinned flag.

        Args:
            thread: Thread instance to update.
            status: True to pin the thread, False to unpin it.
        """
        thread.is_pinned = status
        self.session.add(thread)
        await self.session.flush()

    async def delete_thread(
            self,
            thread: Thread
    ) -> None:
        """Deletes a thread.

        Args:
            thread: Thread instance to delete.
        """
        await self.session.delete(thread)
        await self.session.flush()

    async def get_session_milestone_threads(
            self,
            session_id: int,
            milestone_id: int
    ) -> list[Thread]:
        """Lists threads scoped to a specific session and milestone.

        Args:
            session_id: ID of the reading session to filter by.
            milestone_id: ID of the milestone to filter by.

        Returns:
            List of matching Thread instances.
        """
        stmt = select(Thread).where(
            and_(
                Thread.session_id == session_id,
                Thread.milestone_id == milestone_id
            )
        )
        result = await self.session.execute(stmt)
        threads = result.scalars().all()
        return threads

    async def get_club_general_threads(
            self,
            club_id: int,
    ) -> list[Thread]:
        """Lists a club's general threads, pinned threads first.

        Args:
            club_id: ID of the club to list threads for.

        Returns:
            List of matching Thread instances.
        """
        stmt = select(Thread).where(
            and_(
                Thread.club_id == club_id,
                Thread.is_general == True
            )
        ).order_by(desc(Thread.is_pinned))
        result = await self.session.execute(stmt)
        threads = result.scalars().all()
        return threads

    async def get_thread_by_id(
            self,
            thread_id: int
    ) -> Thread | None:
        """Fetches a single thread by ID.

        Args:
            thread_id: ID of the thread to fetch.

        Returns:
            Matching Thread instance, or None if not found.
        """
        stmt = select(Thread).where(Thread.id == thread_id)
        result = await self.session.execute(stmt)
        thread = result.scalar_one_or_none()
        return thread
