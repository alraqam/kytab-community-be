from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_member
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.reading_session.exceptions import DiscussionPromptNotFoundError
from src.backend.clubs.reading_session.models import Milestone, DiscussionPrompt
from src.backend.clubs.reading_session.repository.prompt import DiscussionPromptRepository
from src.backend.clubs.reading_session.schemas import CreateDiscussionPrompt, UpdateDiscussionPrompt
from src.backend.identity.auth.models import User


class DiscussionPromptManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.prompt_repo = DiscussionPromptRepository(session)
        self.club_manager = ClubManager(session)

    async def create_prompt(
            self,
            user: User,
            club: Club,
            milestone: Milestone,
            request: CreateDiscussionPrompt
    ) -> DiscussionPrompt:
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
        await is_club_member(club, user, self.session)
        return await self.prompt_repo.get_milestone_prompts(milestone.id)

    async def get_prompt_by_id(
            self,
            prompt_id: int,
    ) -> DiscussionPrompt:
        result = await self.prompt_repo.get_prompt_by_id(prompt_id)
        if not result:
            raise DiscussionPromptNotFoundError("Discussion prompt not found")
        return result
