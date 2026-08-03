from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.exceptions import IsNotProgressOwner, ProgressNotInMilestone, \
    MilestoneNotInReadingSessionError, ReadingSessionNotInClubError, PromptNotInMilestoneError
from src.backend.clubs.reading_session.models import MilestoneProgress, DiscussionPrompt
from src.backend.identity.auth.models import User
from src.backend.clubs.reading_session.managers.milestone import MilestoneManager
from src.backend.clubs.reading_session.managers.session import ReadingSessionManager
from src.backend.clubs.reading_session.models import ReadingSession, Milestone
from src.backend.core.dependencies import get_db


async def get_reading_session_manager(
        session: AsyncSession = Depends(get_db)
) -> ReadingSessionManager:
    """Builds a ReadingSessionManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        ReadingSessionManager instance.
    """
    return ReadingSessionManager(session)

async def get_reading_session_or_404(
        session_id: int,
        club: Club = Depends(get_club_or_404),
        manager: ReadingSessionManager = Depends(get_reading_session_manager)
) -> ReadingSession:
    """Resolves a reading session by path parameter, raising if it doesn't exist or belongs to another club.

    Args:
        session_id: ID of the reading session from the path.
        club: Club instance resolved via get_club_or_404.
        manager: ReadingSessionManager used to look up the session.

    Returns:
        ReadingSession instance.

    Raises:
        ReadingSessionNotFound: When no reading session matches the ID.
        ReadingSessionNotInClubError: When the session does not belong to the given club.
    """
    session = await manager.get_session_by_id(session_id)
    if session.club_id != club.id:
        raise ReadingSessionNotInClubError("Reading session not found in this club")
    return session

async def get_milestone_manager(
        session: AsyncSession = Depends(get_db)
) -> MilestoneManager:
    """Builds a MilestoneManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        MilestoneManager instance.
    """
    return MilestoneManager(session)

async def get_milestone_or_404(
        milestone_id: int,
        session: ReadingSession = Depends(get_reading_session_or_404),
        manager: MilestoneManager = Depends(get_milestone_manager)
) -> Milestone:
    """Resolves a milestone by path parameter, raising if it doesn't exist or belongs to another session.

    Args:
        milestone_id: ID of the milestone from the path.
        session: ReadingSession instance resolved via get_reading_session_or_404.
        manager: MilestoneManager used to look up the milestone.

    Returns:
        Milestone instance.

    Raises:
        MilestoneNotFoundError: When no milestone matches the ID.
        MilestoneNotInReadingSessionError: When the milestone does not belong to the given session.
    """
    milestone = await manager.get_milestone_by_id(milestone_id)
    if milestone.session_id != session.id:
        raise MilestoneNotInReadingSessionError("Milestone not found in this reading session")
    return milestone

async def is_milestone_progress_owner(
        progress: MilestoneProgress,
        user: User,
):
    """Checks that the given user owns the milestone progress record.

    Args:
        progress: MilestoneProgress instance to check.
        user: User to verify ownership for.

    Returns:
        True if the user owns the progress record.

    Raises:
        IsNotProgressOwner: When the user does not own the progress record.
    """
    if progress.user_id != user.id:
        raise IsNotProgressOwner("Is not milestone progress owner")
    return True

from src.backend.clubs.reading_session.managers.progress import MilestoneProgressManager

async def get_milestone_progress_manager(
        session: AsyncSession = Depends(get_db)
) -> MilestoneProgressManager:
    """Builds a MilestoneProgressManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        MilestoneProgressManager instance.
    """
    return MilestoneProgressManager(session)

async def get_milestone_progress_or_404(
        progress_id: int,
        milestone: Milestone = Depends(get_milestone_or_404),
        manager: MilestoneProgressManager = Depends(get_milestone_progress_manager)
) -> MilestoneProgress:
    """Resolves a milestone progress record by path parameter, raising if it doesn't exist or belongs to another milestone.

    Args:
        progress_id: ID of the milestone progress record from the path.
        milestone: Milestone instance resolved via get_milestone_or_404.
        manager: MilestoneProgressManager used to look up the progress record.

    Returns:
        MilestoneProgress instance.

    Raises:
        MilestoneProgressNotFound: When no progress record matches the ID.
        ProgressNotInMilestone: When the progress record does not belong to the given milestone.
    """
    progress = await manager.get_milestone_by_id(progress_id)
    if progress.milestone_id != milestone.id:
        raise ProgressNotInMilestone("Progress not found in this milestone")
    return progress

from src.backend.clubs.reading_session.managers.prompt import DiscussionPromptManager

async def get_discussion_prompt_manager(
        session: AsyncSession = Depends(get_db)
) -> DiscussionPromptManager:
    """Builds a DiscussionPromptManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        DiscussionPromptManager instance.
    """
    return DiscussionPromptManager(session)

async def get_discussion_prompt_or_404(
        prompt_id: int,
        milestone: Milestone = Depends(get_milestone_or_404),
        manager: DiscussionPromptManager = Depends(get_discussion_prompt_manager)
) -> DiscussionPrompt:
    """Resolves a discussion prompt by path parameter, raising if it doesn't exist or belongs to another milestone.

    Args:
        prompt_id: ID of the discussion prompt from the path.
        milestone: Milestone instance resolved via get_milestone_or_404.
        manager: DiscussionPromptManager used to look up the prompt.

    Returns:
        DiscussionPrompt instance.

    Raises:
        DiscussionPromptNotFoundError: When no prompt matches the ID.
        PromptNotInMilestoneError: When the prompt does not belong to the given milestone.
    """
    prompt = await manager.get_prompt_by_id(prompt_id)
    if prompt.milestone_id != milestone.id:
        raise PromptNotInMilestoneError("Prompt not found in this milestone")
    return prompt
