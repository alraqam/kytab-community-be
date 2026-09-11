from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import RecoveryCode


@dataclass
class RecoveryCodeRepository:
    """Data-access layer for two-factor recovery code persistence and queries."""

    session: AsyncSession

    async def create_many(
            self,
            user_id: int,
            code_hashes: list[str],
    ) -> list[RecoveryCode]:
        """Inserts a batch of hashed recovery codes for a user.

        Args:
            user_id: ID of the user the recovery codes belong to.
            code_hashes: Hashed recovery code strings to store.

        Returns:
            List of newly created RecoveryCode instances.
        """
        stmt = insert(RecoveryCode).values(
            [{"user_id": user_id, "code_hash": code_hash} for code_hash in code_hashes]
        ).returning(RecoveryCode)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return list(result.scalars().all())

    async def get_unused_by_user(
            self,
            user_id: int,
    ) -> list[RecoveryCode]:
        """Lists a user's unused recovery codes.

        Args:
            user_id: ID of the user whose recovery codes are being listed.

        Returns:
            List of unused RecoveryCode instances belonging to the user.
        """
        stmt = select(RecoveryCode).where(
            and_(
                RecoveryCode.user_id == user_id,
                RecoveryCode.used_at == None,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_used(
            self,
            recovery_code: RecoveryCode,
    ) -> None:
        """Stamps a recovery code as used and flushes the session.

        Args:
            recovery_code: RecoveryCode instance to mark used.
        """
        recovery_code.used_at = datetime.now(timezone.utc)
        self.session.add(recovery_code)
        await self.session.flush()

    async def delete_all_for_user(
            self,
            user_id: int,
    ) -> None:
        """Deletes all recovery codes belonging to a user.

        Args:
            user_id: ID of the user whose recovery codes are being deleted.
        """
        stmt = select(RecoveryCode).where(RecoveryCode.user_id == user_id)
        result = await self.session.execute(stmt)
        for recovery_code in result.scalars().all():
            await self.session.delete(recovery_code)
        await self.session.flush()
