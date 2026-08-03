from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.thread.models import PostReaction

@dataclass
class PostReactionRepository:
    """Data-access layer for post reaction persistence and queries."""

    session: AsyncSession

    async def create_reaction(
            self,
            post_id: int,
            user_id: int,
            emoji: str,
    ) -> PostReaction:
        """Inserts a new reaction on a post.

        Args:
            post_id: ID of the post being reacted to.
            user_id: ID of the user creating the reaction.
            emoji: Emoji representing the reaction.

        Returns:
            Newly created PostReaction instance.
        """
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
        """Deletes a reaction.

        Args:
            reaction: PostReaction instance to delete.
        """
        await self.session.delete(reaction)
        await self.session.flush()

    async def get_post_reactions(
            self,
            post_id: int,
    ) -> list[PostReaction]:
        """Lists all reactions on a post.

        Args:
            post_id: ID of the post to list reactions for.

        Returns:
            List of matching PostReaction instances.
        """
        stmt = select(PostReaction).where(PostReaction.post_id == post_id)
        result = await self.session.execute(stmt)
        reactions = result.scalars().all()
        return reactions

    async def get_reaction_by_id(
            self,
            reaction_id: int
    ) -> PostReaction | None:
        """Fetches a single reaction by ID.

        Args:
            reaction_id: ID of the reaction to fetch.

        Returns:
            Matching PostReaction instance, or None if not found.
        """
        stmt = select(PostReaction).where(PostReaction.id == reaction_id)
        result = await self.session.execute(stmt)
        reaction = result.scalar_one_or_none()
        return reaction
