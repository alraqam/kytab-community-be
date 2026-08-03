from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_club_member
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.dependencies import is_milestone_progress_owner
from src.backend.clubs.reading_session.exceptions import ActiveSessionError, MilestoneProgressNotFound, \
    MilestoneProgressAlreadyExists
from src.backend.clubs.reading_session.managers.session import ReadingSessionManager
from src.backend.clubs.reading_session.models import ReadingSession, Milestone, MilestoneProgress
from src.backend.clubs.reading_session.repository.progress import MilestoneProgressRepository
from src.backend.identity.auth.models import User


class MilestoneProgressManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.progress_repo = MilestoneProgressRepository(session)
        self.session_manager = ReadingSessionManager(session)

    async def create_milestone_progress(
            self,
            user: User,
            club: Club,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> MilestoneProgress:
        await is_club_member(club, user, self.session)

        if reading_session.completed_at:
            raise ActiveSessionError("Session must be active")

        try:
            response = await self.progress_repo.create_milestone_progress(
                session_id=reading_session.id,
                milestone_id=milestone.id,
                user_id=user.id,
            )
        except IntegrityError:
            raise MilestoneProgressAlreadyExists("Milestone progress for this session already exists")

        await self.session.commit()
        return response

    async def update_milestone_progress(
            self,
            progress: MilestoneProgress,
            user: User,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> None:
        await is_milestone_progress_owner(progress, user)

        if reading_session.completed_at:
            raise ActiveSessionError("Session must be active")

        await self.progress_repo.update_milestone_progress(
            progress=progress,
            milestone_id=milestone.id,
        )
        await self.session.commit()

    async def finish_milestone_progress(
            self,
            progress: MilestoneProgress,
            user: User,
    ) -> None:
        await is_milestone_progress_owner(progress, user)

        await self.progress_repo.update_milestone_progress_finished(
            progress=progress,
            status=True
        )
        await self.session.commit()

    async def delete_milestone_progress(
            self,
            progress: MilestoneProgress,
            user: User,
    ) -> None:
        await is_milestone_progress_owner(progress, user)

        await self.progress_repo.delete_milestone_progress(
            progress=progress,
        )
        await self.session.commit()

    async def get_user_milestone_progress(
            self,
            reading_session: ReadingSession,
            user: User,
    ) -> MilestoneProgress:
        progress = await self.progress_repo.get_user_milestone_progress(
            session_id=reading_session.id,
            user_id=user.id,
        )
        if not progress:
            raise MilestoneProgressNotFound("Milestone progress not found")
        return progress

    async def get_session_milestone_progress(
            self,
            reading_session: ReadingSession,
            user: User,
            club: Club,
    ) -> list[MilestoneProgress]:
        await is_club_member(club, user, self.session)

        progress = await self.progress_repo.get_session_milestone_progress(
            session_id=reading_session.id,
        )
        return progress

    async def get_milestone_by_id(
            self,
            progress_id: int,
    ) -> MilestoneProgress:
        progress = await self.progress_repo.get_milestone_progress_by_id(
            progress_id=progress_id
        )
        if not progress:
            raise MilestoneProgressNotFound("Milestone progress not found")
        return progress