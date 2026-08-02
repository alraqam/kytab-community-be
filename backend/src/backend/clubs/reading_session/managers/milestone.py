from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.exceptions import MilestoneValueError
from src.backend.clubs.reading_session.schemas import MilestoneBoundaryType
from src.backend.clubs.reading_session.filters import MilestoneFilter
from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_member
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.reading_session.exceptions import DateInPastError, MilestoneAlreadyExistsError, \
    MilestoneNotFoundError
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.clubs.reading_session.repository.milestone import MilestoneRepository
from src.backend.clubs.reading_session.schemas import CreateMilestone, UpdateMilestone
from src.backend.clubs.club_membership.managers.membership import ClubMembershipManager
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType


class MilestoneManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.milestone_repo = MilestoneRepository(session)
        self.club_manager = ClubManager(session)
        self.membership_manager = ClubMembershipManager(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)

    async def _notify_schedule_change(
            self,
            user: User,
            club,
            title: str,
            object_id: int,
    ) -> None:
        memberships = await self.membership_manager.get_memberships(club, user)
        recipients = [
            await self.user_manager.get_user_by_id(membership.user_id)
            for membership in memberships
            if membership.user_id != user.id
        ]
        await self.notification_manager.notify_many(
            recipients,
            category=NotificationCategory.general,
            title=title,
            object_type=NotificationObjectType.milestone,
            object_id=object_id,
            club_id=club.id,
        )

    async def create_milestone(
            self,
            user: User,
            reading_session: ReadingSession,
            request: CreateMilestone
    ) -> Milestone:
        club = await self.club_manager.get_club_by_id(reading_session.club_id)
        is_owner_or_moderator(club, user.id)

        if request.target_date <= reading_session.created_at.date() or request.target_date > reading_session.deadline.date():
            raise DateInPastError("Milestone target date can not be before reading session")

        exists = await self.milestone_repo.exists_milestone(reading_session.id, request.boundary_type, request.boundary_value)
        if exists:
            raise MilestoneAlreadyExistsError("Milestone already exists")

        if request.boundary_type == MilestoneBoundaryType.percent and request.boundary_value > 100:
            raise MilestoneValueError("Milestone percent value can not be greater than 100")

        response = await self.milestone_repo.create_milestone(
            session_id=reading_session.id,
            label=request.label,
            boundary_type=request.boundary_type,
            boundary_value=request.boundary_value,
            target_date=request.target_date,
            order_index=request.order_index,
        )

        await self.session.commit()

        await self._notify_schedule_change(
            user, club,
            title=f"Reading schedule updated in {club.name}: milestone \"{response.label}\" added",
            object_id=response.id,
        )
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

        if request.target_date <= reading_session.created_at.date() or request.target_date > reading_session.deadline.date():
            raise DateInPastError("Milestone target date can not be before reading session")

        if request.boundary_value and request.boundary_type:
            exists = await self.milestone_repo.exists_milestone(reading_session.id, request.boundary_type, request.boundary_value)
            if exists:
                raise MilestoneAlreadyExistsError("Milestone already exists")

        if request.boundary_type == MilestoneBoundaryType.percent and request.boundary_value > 100:
            raise MilestoneValueError("Milestone percent value can not be greater than 100")

        await self.milestone_repo.update_milestone(
            milestone=milestone,
            label=request.label,
            boundary_type=request.boundary_type,
            boundary_value=request.boundary_value,
            target_date=request.target_date,
            order_index=request.order_index,
        )
        await self.session.commit()

        await self._notify_schedule_change(
            user, club,
            title=f"Reading schedule updated in {club.name}: milestone \"{milestone.label}\" changed",
            object_id=milestone.id,
        )

    async def delete_milestone(
            self,
            user: User,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> None:
        club = await self.club_manager.get_club_by_id(reading_session.club_id)
        is_owner_or_moderator(club, user.id)

        milestone_id = milestone.id
        milestone_label = milestone.label
        await self.milestone_repo.delete_milestone(
            milestone=milestone,
        )
        await self.session.commit()

        await self._notify_schedule_change(
            user, club,
            title=f"Reading schedule updated in {club.name}: milestone \"{milestone_label}\" removed",
            object_id=milestone_id,
        )

    async def get_session_milestones(
            self,
            reading_session: ReadingSession,
            club: Club,
            user: User,
            filters: MilestoneFilter
    ) -> list[Milestone]:
        await is_club_member(club, user, self.session)
        milestones = await self.milestone_repo.get_session_milestones(
            session_id=reading_session.id,
            filters=filters
        )
        return milestones

    async def get_milestone_by_id(
            self,
            milestone_id: int,
    ) -> Milestone:
        milestone = await self.milestone_repo.get_milestone_by_id(
            milestone_id=milestone_id,
        )
        if not milestone:
            raise MilestoneNotFoundError("Milestone not found")
        return milestone