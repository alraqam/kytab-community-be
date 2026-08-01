from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.consent.models import ConsentRecords


@dataclass
class ConsentRepository:
    session: AsyncSession

    async def create_consent(
            self,
            user_id: int,
            document_id: int,
    ) -> ConsentRecords:
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
        stmt = select(ConsentRecords).where(ConsentRecords.user_id == user_id)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_consent_by_id(
            self,
            consent_id: int
    ) -> ConsentRecords | None:
        stmt = select(ConsentRecords).where(ConsentRecords.id == consent_id)
        result = await self.session.execute(stmt)
        consent = result.scalar_one_or_none()
        return consent

