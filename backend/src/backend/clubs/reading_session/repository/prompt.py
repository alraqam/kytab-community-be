from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.models import DiscussionPrompt


@dataclass
class DiscussionPromptRepository:
    """Data-access layer for discussion prompt persistence and queries."""

    session: AsyncSession

    async def create_prompt(
            self,
            milestone_id: int,
            created_by_id: int,
            text: str,
    ) -> DiscussionPrompt:
        """Inserts a new discussion prompt.

        Args:
            milestone_id: ID of the milestone the prompt is attached to.
            created_by_id: ID of the user creating the prompt.
            text: Prompt text.

        Returns:
            Newly created DiscussionPrompt instance.
        """
        result = DiscussionPrompt(
            milestone_id=milestone_id,
            created_by_id=created_by_id,
            text=text,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_prompt(
            self,
            prompt: DiscussionPrompt,
            text: str | None = None,
    ) -> None:
        """Updates a discussion prompt's text, skipping if unset.

        Args:
            prompt: DiscussionPrompt instance to update.
            text: New prompt text, or None to leave unchanged.
        """
        if text is not None:
            prompt.text = text
        self.session.add(prompt)
        await self.session.flush()

    async def delete_prompt(
            self,
            prompt: DiscussionPrompt,
    ) -> None:
        """Deletes a discussion prompt.

        Args:
            prompt: DiscussionPrompt instance to delete.
        """
        await self.session.delete(prompt)
        await self.session.flush()

    async def get_milestone_prompts(
            self,
            milestone_id: int,
    ) -> list[DiscussionPrompt]:
        """Lists all discussion prompts for a milestone.

        Args:
            milestone_id: ID of the milestone.

        Returns:
            List of matching DiscussionPrompt instances.
        """
        stmt = select(DiscussionPrompt).where(DiscussionPrompt.milestone_id == milestone_id)
        result = await self.session.execute(stmt)
        prompts = result.scalars().all()
        return prompts

    async def get_prompt_by_id(
            self,
            prompt_id: int,
    ) -> DiscussionPrompt | None:
        """Fetches a single discussion prompt by ID.

        Args:
            prompt_id: ID of the prompt to fetch.

        Returns:
            Matching DiscussionPrompt instance, or None if not found.
        """
        stmt = select(DiscussionPrompt).where(DiscussionPrompt.id == prompt_id)
        result = await self.session.execute(stmt)
        prompt = result.scalar_one_or_none()
        return prompt