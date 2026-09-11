from dataclasses import dataclass

from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import OAuthAccount


@dataclass
class OAuthAccountRepository:
    """Data-access layer for OAuth account persistence and queries."""

    session: AsyncSession

    async def get_by_provider_subject(
            self,
            provider: str,
            provider_user_id: str,
    ) -> OAuthAccount | None:
        """Fetches a linked OAuth account by provider and provider-side subject ID.

        Args:
            provider: OAuth provider name.
            provider_user_id: Provider-side unique subject identifier ("sub" claim).

        Returns:
            Matching OAuthAccount instance, or None if not linked yet.
        """
        stmt = select(OAuthAccount).where(
            and_(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
            self,
            user_id: int,
            provider: str,
            provider_user_id: str,
    ) -> OAuthAccount:
        """Links a user to an external OAuth provider account.

        Args:
            user_id: ID of the user to link.
            provider: OAuth provider name.
            provider_user_id: Provider-side unique subject identifier ("sub" claim).

        Returns:
            Newly created OAuthAccount instance.
        """
        stmt = insert(OAuthAccount).values(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
        ).returning(OAuthAccount)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalars().first()
