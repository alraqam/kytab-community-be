from datetime import timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.filters import MilestoneFilter
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.reading_session.exceptions import DateInPastError, MilestoneAlreadyExistsError, \
    MilestoneNotFoundError
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.reading_session.repository.milestone import MilestoneRepository
from src.backend.clubs.reading_session.schemas import CreateMilestone, UpdateMilestone
from src.backend.identity.auth.models import User


class MilestoneManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.milestone_repo = MilestoneRepository(session)
        self.club_manager = ClubManager(session)

    async def create_milestone(
            self,
            user: User,
            reading_session: ReadingSession,
            request: CreateMilestone
    ) -> Milestone:
        club = await self.club_manager.get_club_by_id(reading_session.club_id)
        is_owner_or_moderator(club, user.id)

        if request.target_date <= reading_session.created_at(timezone.utc).date() or request.target_date > reading_session.deadline(timezone.utc).date():
            raise DateInPastError("Milestone target date can not be before reading session")

        exists = await self.milestone_repo.exists_milestone(reading_session.id, request.boundary_type, request.boundary_value)
        if exists:
            raise MilestoneAlreadyExistsError("Milestone already exists")

        response = await self.milestone_repo.create_milestone(
            session_id=reading_session.id,
            label=request.label,
            boundary_type=request.boundary_type,
            boundary_value=request.boundary_value,
            target_date=request.target_date,
            order_index=request.order_index,
        )

        await self.session.commit()
        return response

    async def update_milestone(
            self,
            user: User,
            reading_session: ReadingSession,
            milestone: Milestone,
            request: UpdateMilestone
    ) -> None:
        club = await self.club_manager.get_club_by_id(reading_session.club_id)
        is_owner_or_moderator(club, user.id)

        await self.milestone_repo.update_milestone(
            milestone=milestone,
            label=request.label,
            boundary_type=request.boundary_type,
            boundary_value=request.boundary_value,
            target_date=request.target_date,
            order_index=request.order_index,
        )
        await self.session.commit()

    async def delete_milestone(
            self,
            user: User,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> None:
        club = await self.club_manager.get_club_by_id(reading_session.club_id)
        is_owner_or_moderator(club, user.id)

        await self.milestone_repo.delete_milestone(
            milestone=milestone,
        )
        await self.session.commit()

    async def get_session_milestones(
            self,
            reading_session: ReadingSession,
            filters: MilestoneFilter
    ) -> list[Milestone]:
        milestones = await self.milestone_repo.get_session_milestones(
            session_id=reading_session.id,
            filters=filters
        )
        return milestones

    async def get_milestone_by_id(
            self,
            milestone_id: int,
    ) -> Milestone | None:
        milestone = await self.milestone_repo.get_milestone_by_id(
            milestone_id=milestone_id,
        )
        if not milestone:
            raise MilestoneNotFoundError("Milestone not found")
        return milestone