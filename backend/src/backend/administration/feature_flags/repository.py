from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.feature_flags.filters import FeatureFlagFilter
from src.backend.administration.feature_flags.models import FeatureFlag


@dataclass
class FeatureFlagRepository:
    """Data-access layer for feature flag persistence and queries."""

    session: AsyncSession

    async def create_feature_flag(
            self,
            created_by_id: int,
            key: str,
            name: str,
            description: str | None,
            rollout_percentage: int,
    ) -> FeatureFlag:
        """Inserts a new disabled feature flag.

        Args:
            created_by_id: ID of the admin user creating the flag.
            key: Unique identifier used by clients to evaluate the flag.
            name: Human-readable flag name.
            description: Optional flag description.
            rollout_percentage: Percentage of users to enable the flag for once enabled.

        Returns:
            Newly created FeatureFlag instance.
        """
        result = FeatureFlag(
            created_by_id=created_by_id,
            key=key,
            name=name,
            description=description,
            is_enabled=False,
            rollout_percentage=rollout_percentage,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_feature_flag(
            self,
            flag: FeatureFlag,
            name: str | None = None,
            description: str | None = None,
            rollout_percentage: int | None = None,
    ) -> None:
        """Updates the given fields of a feature flag, skipping unset ones.

        Args:
            flag: FeatureFlag instance to update.
            name: New name, or None to leave unchanged.
            description: New description, or None to leave unchanged.
            rollout_percentage: New rollout percentage, or None to leave unchanged.
        """
        updates = {
            "name": name,
            "description": description,
            "rollout_percentage": rollout_percentage,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(flag, field, value)
        await self.session.flush()

    async def update_enabled_status(
            self,
            flag: FeatureFlag,
            status: bool,
    ) -> None:
        """Sets a feature flag's enabled state.

        Args:
            flag: FeatureFlag instance to update.
            status: True to enable, False to disable.
        """
        flag.is_enabled = status
        self.session.add(flag)
        await self.session.flush()

    async def delete_feature_flag(
            self,
            flag: FeatureFlag,
    ) -> None:
        """Deletes a feature flag.

        Args:
            flag: FeatureFlag instance to delete.
        """
        await self.session.delete(flag)
        await self.session.flush()

    async def get_feature_flags(
            self,
            filters: FeatureFlagFilter | None = None,
    ) -> list[FeatureFlag]:
        """Lists feature flags, optionally filtered and sorted.

        Args:
            filters: FeatureFlagFilter to apply, or None for no filtering.

        Returns:
            List of matching FeatureFlag instances.
        """
        stmt = select(FeatureFlag)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_enabled_feature_flags(
            self,
    ) -> list[FeatureFlag]:
        """Lists all enabled feature flags.

        Returns:
            List of enabled FeatureFlag instances.
        """
        stmt = select(FeatureFlag).where(FeatureFlag.is_enabled == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_feature_flag_by_id(
            self,
            flag_id: int,
    ) -> FeatureFlag | None:
        """Fetches a single feature flag by ID.

        Args:
            flag_id: ID of the feature flag to fetch.

        Returns:
            Matching FeatureFlag instance, or None if not found.
        """
        stmt = select(FeatureFlag).where(FeatureFlag.id == flag_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
