from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.reading_session.models import DiscussionPrompt


@dataclass
class DiscussionPromptRepository:
    session: AsyncSession

    async def create_prompt(
            self,
            milestone_id: int,
            created_by_id: int,
            text: str,
    ) -> DiscussionPrompt:
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
        if text is not None:
            prompt.text = text
        self.session.add(prompt)
        await self.session.flush()

    async def delete_prompt(
            self,
            prompt: DiscussionPrompt,
    ) -> None:
        await self.session.delete(prompt)
        await self.session.flush()

    async def get_milestone_prompts(
            self,
            milestone_id: int,
    ) -> list[DiscussionPrompt]:
        stmt = select(DiscussionPrompt).where(DiscussionPrompt.milestone_id == milestone_id)
        result = await self.session.execute(stmt)
        prompts = result.scalars().all()
        return prompts

    async def get_prompt_by_id(
            self,
            prompt_id: int,
    ) -> DiscussionPrompt | None:
        stmt = select(DiscussionPrompt).where(DiscussionPrompt.id == prompt_id)
        result = await self.session.execute(stmt)
        prompt = result.scalar_one_or_none()
        return prompt