from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_member
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.core.storage import StorageService
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.exceptions import DiscussionPromptNotFoundError
from src.backend.clubs.reading_session.models import Milestone, DiscussionPrompt
from src.backend.clubs.reading_session.repository.prompt import DiscussionPromptRepository
from src.backend.clubs.reading_session.schemas import CreateDiscussionPrompt, UpdateDiscussionPrompt
from src.backend.identity.auth.models import User


class DiscussionPromptManager:
    """Handles business logic for milestone discussion prompts: creation, updates, deletion, and retrieval."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.prompt_repo = DiscussionPromptRepository(session)
        self.club_manager = ClubManager(session, StorageService())

    async def create_prompt(
            self,
            user: User,
            club: Club,
            milestone: Milestone,
            request: CreateDiscussionPrompt
    ) -> DiscussionPrompt:
        """Creates a new discussion prompt for a milestone.

        Args:
            user: Owner or moderator creating the prompt.
            club: Club the milestone belongs to.
            milestone: Milestone the prompt is attached to.
            request: CreateDiscussionPrompt payload with the prompt text.

        Returns:
            Newly created DiscussionPrompt instance.

        Raises:
            IsNotClubOwnerError: When the user is not the club owner or a moderator.
        """
        is_owner_or_moderator(club, user.id)

        result = await self.prompt_repo.create_prompt(
            milestone_id=milestone.id,
            created_by_id=user.id,
            text=request.text,
        )
        await self.session.commit()
        return result

    async def update_prompt(
            self,
            user: User,
            club: Club,
            prompt: DiscussionPrompt,
            request: UpdateDiscussionPrompt
    ) -> None:
        """Updates a discussion prompt's text.

        Args:
            user: Owner or moderator updating the prompt.
            club: Club the prompt belongs to.
            prompt: DiscussionPrompt instance to update.
            request: UpdateDiscussionPrompt payload with the new text.

        Raises:
            IsNotClubOwnerError: When the user is not the club owner or a moderator.
        """
        is_owner_or_moderator(club, user.id)

        await self.prompt_repo.update_prompt(
            prompt=prompt,
            text=request.text,
        )
        await self.session.commit()

    async def delete_prompt(
            self,
            user: User,
            club: Club,
            prompt: DiscussionPrompt,
    ) -> None:
        """Deletes a discussion prompt.

        Args:
            user: Owner or moderator deleting the prompt.
            club: Club the prompt belongs to.
            prompt: DiscussionPrompt instance to delete.

        Raises:
            IsNotClubOwnerError: When the user is not the club owner or a moderator.
        """
        is_owner_or_moderator(club, user.id)

        await self.prompt_repo.delete_prompt(
            prompt=prompt,
        )
        await self.session.commit()

    async def get_milestone_prompts(
            self,
            user: User,
            club: Club,
            milestone: Milestone,
    ) -> list[DiscussionPrompt]:
        """Lists all discussion prompts for a milestone.

        Args:
            user: User requesting the prompts; must be a club member.
            club: Club the milestone belongs to.
            milestone: Milestone whose prompts are listed.

        Returns:
            List of matching DiscussionPrompt instances.

        Raises:
            NotClubMemberError: When the user is not a member of the club.
        """
        await is_club_member(club, user, self.session)
        return await self.prompt_repo.get_milestone_prompts(milestone.id)

    async def get_prompt_by_id(
            self,
            prompt_id: int,
    ) -> DiscussionPrompt:
        """Fetches a discussion prompt by ID.

        Args:
            prompt_id: ID of the prompt to fetch.

        Returns:
            Matching DiscussionPrompt instance.

        Raises:
            DiscussionPromptNotFoundError: When no prompt matches the ID.
        """
        result = await self.prompt_repo.get_prompt_by_id(prompt_id)
        if not result:
            raise DiscussionPromptNotFoundError("Discussion prompt not found")
        return result
