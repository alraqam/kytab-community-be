from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.models import PostReaction

@dataclass
class PostReactionRepository:
    session: AsyncSession

    async def create_reaction(
            self,
            post_id: int,
            user_id: int,
            emoji: str,
    ) -> PostReaction:
        result = PostReaction(
            post_id=post_id,
            user_id=user_id,
            emoji=emoji,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def delete_reaction(
            self,
            reaction: PostReaction
    ) -> None:
        await self.session.delete(reaction)
        await self.session.flush()

    async def get_post_reactions(
            self,
            post_id: int,
    ) -> list[PostReaction]:
        stmt = select(PostReaction).where(PostReaction.post_id == post_id)
        result = await self.session.execute(stmt)
        reactions = result.scalars().all()
        return reactions

    async def get_reaction_by_id(
            self,
            reaction_id: int
    ) -> PostReaction | None:
        stmt = select(PostReaction).where(PostReaction.id == reaction_id)
        result = await self.session.execute(stmt)
        reaction = result.scalar_one_or_none()
        return reaction

