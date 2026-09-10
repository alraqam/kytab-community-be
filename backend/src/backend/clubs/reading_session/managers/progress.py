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
from src.backend.clubs.reading_session.repository.prompt import DiscussionPromptRepository
from src.backend.identity.auth.models import User
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType


class MilestoneProgressManager:
    """Handles business logic for tracking a user's progress through reading session milestones."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.progress_repo = MilestoneProgressRepository(session)
        self.session_manager = ReadingSessionManager(session)
        self.prompt_repo = DiscussionPromptRepository(session)
        self.notification_manager = NotificationManager(session)

    async def create_milestone_progress(
            self,
            user: User,
            club: Club,
            reading_session: ReadingSession,
            milestone: Milestone,
    ) -> MilestoneProgress:
        """Creates a milestone progress record for a club member in an active session.

        Args:
            user: User creating their progress record.
            club: Club the reading session belongs to.
            reading_session: ReadingSession the milestone belongs to.
            milestone: Milestone the user is tracking progress against.

        Returns:
            Newly created MilestoneProgress instance.

        Raises:
            NotClubMemberError: When the user is not a member of the club.
            ActiveSessionError: When the reading session is already completed.
            MilestoneProgressAlreadyExists: When progress for this session already exists.
        """
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
        """Updates which milestone a progress record points to, for the owning user, in an active session.

        Args:
            progress: MilestoneProgress instance to update.
            user: User expected to own the progress record.
            reading_session: ReadingSession the milestone belongs to.
            milestone: New Milestone to associate with the progress record.

        Raises:
            IsNotProgressOwner: When the user does not own the progress record.
            ActiveSessionError: When the reading session is already completed.
        """
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
            reading_session: ReadingSession,
    ) -> None:
        """Marks a milestone progress record as finished, for the owning user.

        Surfaces each discussion prompt attached to the milestone to the user as a
        notification, now that they've reached it.

        Args:
            progress: MilestoneProgress instance to mark finished.
            user: User expected to own the progress record.
            reading_session: ReadingSession the milestone belongs to.

        Raises:
            IsNotProgressOwner: When the user does not own the progress record.
        """
        await is_milestone_progress_owner(progress, user)

        milestone_id = progress.milestone_id
        milestone_label = progress.milestone_label

        await self.progress_repo.update_milestone_progress_finished(
            progress=progress,
            status=True
        )
        await self.session.commit()

        prompts = await self.prompt_repo.get_milestone_prompts(milestone_id)
        for prompt in prompts:
            await self.notification_manager.notify(
                user,
                category=NotificationCategory.discussion_prompt,
                title=f"Discussion prompt unlocked: \"{milestone_label}\"",
                body=prompt.text,
                object_type=NotificationObjectType.discussion_prompt,
                object_id=prompt.id,
                club_id=reading_session.club_id,
            )

    async def delete_milestone_progress(
            self,
            progress: MilestoneProgress,
            user: User,
    ) -> None:
        """Deletes a milestone progress record, for the owning user.

        Args:
            progress: MilestoneProgress instance to delete.
            user: User expected to own the progress record.

        Raises:
            IsNotProgressOwner: When the user does not own the progress record.
        """
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
        """Fetches a user's milestone progress record for a reading session.

        Args:
            reading_session: ReadingSession to look up progress for.
            user: User whose progress record is fetched.

        Returns:
            Matching MilestoneProgress instance.

        Raises:
            MilestoneProgressNotFound: When no progress record exists for the user and session.
        """
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
        """Lists all milestone progress records for a reading session.

        Args:
            reading_session: ReadingSession to list progress for.
            user: User requesting the list; must be a club member.
            club: Club the reading session belongs to.

        Returns:
            List of matching MilestoneProgress instances.

        Raises:
            NotClubMemberError: When the user is not a member of the club.
        """
        await is_club_member(club, user, self.session)

        progress = await self.progress_repo.get_session_milestone_progress(
            session_id=reading_session.id,
        )
        return progress

    async def get_milestone_by_id(
            self,
            progress_id: int,
    ) -> MilestoneProgress:
        """Fetches a milestone progress record by ID.

        Args:
            progress_id: ID of the progress record to fetch.

        Returns:
            Matching MilestoneProgress instance.

        Raises:
            MilestoneProgressNotFound: When no progress record matches the ID.
        """
        progress = await self.progress_repo.get_milestone_progress_by_id(
            progress_id=progress_id
        )
        if not progress:
            raise MilestoneProgressNotFound("Milestone progress not found")
        return progress