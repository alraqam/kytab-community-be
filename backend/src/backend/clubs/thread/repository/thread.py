from dataclasses import dataclass

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.models import Thread


@dataclass
class ThreadRepository:
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
        thread.title = title
        self.session.add(thread)
        await self.session.flush()

    async def update_thread_lock(
            self,
            thread: Thread,
            status: bool,
    ) -> None:
        thread.is_locked = status
        self.session.add(thread)
        await self.session.flush()

    async def update_thread_pin(
            self,
            thread: Thread,
            status: bool,
    ) -> None:
        thread.is_pinned = status
        self.session.add(thread)
        await self.session.flush()

    async def delete_thread(
            self,
            thread: Thread
    ) -> None:
        await self.session.delete(thread)
        await self.session.flush()

    async def get_session_milestone_threads(
            self,
            session_id: int,
            milestone_id: int
    ) -> list[Thread]:
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
        stmt = select(Thread).where(Thread.id == thread_id)
        result = await self.session.execute(stmt)
        thread = result.scalar_one_or_none()
        return thread

