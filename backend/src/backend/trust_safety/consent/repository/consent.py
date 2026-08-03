from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.consent.models import ConsentRecords


@dataclass
class ConsentRepository:
    """Data-access layer for consent record persistence and queries."""

    session: AsyncSession

    async def create_consent(
            self,
            user_id: int,
            document_id: int,
    ) -> ConsentRecords:
        """Inserts a new consent record.

        Args:
            user_id: ID of the user giving consent.
            document_id: ID of the legal document being consented to.

        Returns:
            Newly created ConsentRecords instance.
        """
        result = ConsentRecords(
            user_id = user_id,
            document_id = document_id
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_user_consents(
            self,
            user_id: int
    ) -> list[ConsentRecords]:
        """Lists all consent records belonging to a user.

        Args:
            user_id: ID of the user whose consents to list.

        Returns:
            List of ConsentRecords instances.
        """
        stmt = select(ConsentRecords).where(ConsentRecords.user_id == user_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_consent_by_id(
            self,
            consent_id: int
    ) -> ConsentRecords | None:
        """Fetches a single consent record by ID.

        Args:
            consent_id: ID of the consent record to fetch.

        Returns:
            Matching ConsentRecords instance, or None if not found.
        """
        stmt = select(ConsentRecords).where(ConsentRecords.id == consent_id)
        result = await self.session.execute(stmt)
        consent = result.scalar_one_or_none()
        return consent

