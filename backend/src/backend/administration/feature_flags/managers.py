import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.administration.feature_flags.exceptions import FeatureFlagNotFoundError
from src.backend.administration.feature_flags.filters import FeatureFlagFilter
from src.backend.administration.feature_flags.models import FeatureFlag
from src.backend.administration.feature_flags.repository import FeatureFlagRepository
from src.backend.administration.feature_flags.schemas import CreateFeatureFlag, UpdateFeatureFlag
from src.backend.identity.auth.models import User


def _bucket_for(key: str, user_id: int) -> int:
    """Deterministically maps a (flag key, user) pair to a stable bucket in [0, 100).

    Using a stable hash rather than randomness means the same user consistently
    lands on the same side of the rollout percentage across requests, instead of
    flapping in and out of a staged rollout.

    Args:
        key: Feature flag key.
        user_id: ID of the user being bucketed.

    Returns:
        Integer bucket in the range [0, 100).
    """
    digest = hashlib.sha256(f"{key}:{user_id}".encode()).hexdigest()
    return int(digest, 16) % 100

class FeatureFlagManager:
    """Handles feature flag business logic: creation, rollout, and evaluation."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.feature_flag_repo = FeatureFlagRepository(session)

    async def create_feature_flag(
            self,
            user: User,
            request: CreateFeatureFlag,
    ) -> FeatureFlag:
        """Creates a new feature flag authored by the given user.

        Args:
            user: Admin user creating the flag.
            request: CreateFeatureFlag payload with key, name, description, and rollout percentage.

        Returns:
            Newly created FeatureFlag instance.
        """
        result = await self.feature_flag_repo.create_feature_flag(
            created_by_id=user.id,
            key=request.key,
            name=request.name,
            description=request.description,
            rollout_percentage=request.rollout_percentage,
        )
        await self.session.commit()
        result.created_by_username = user.username
        return result

    async def update_feature_flag(
            self,
            flag: FeatureFlag,
            request: UpdateFeatureFlag,
    ) -> None:
        """Updates a feature flag's name, description, and/or rollout percentage.

        Args:
            flag: FeatureFlag instance to update.
            request: UpdateFeatureFlag payload with the fields to change.
        """
        await self.feature_flag_repo.update_feature_flag(
            flag=flag,
            name=request.name,
            description=request.description,
            rollout_percentage=request.rollout_percentage,
        )
        await self.session.commit()

    async def enable_feature_flag(
            self,
            flag: FeatureFlag,
    ) -> None:
        """Enables a feature flag for rollout.

        Args:
            flag: FeatureFlag instance to enable.
        """
        await self.feature_flag_repo.update_enabled_status(flag, True)
        await self.session.commit()

    async def disable_feature_flag(
            self,
            flag: FeatureFlag,
    ) -> None:
        """Disables a feature flag, hiding it from all users regardless of rollout percentage.

        Args:
            flag: FeatureFlag instance to disable.
        """
        await self.feature_flag_repo.update_enabled_status(flag, False)
        await self.session.commit()

    async def delete_feature_flag(
            self,
            flag: FeatureFlag,
    ) -> None:
        """Permanently deletes a feature flag.

        Args:
            flag: FeatureFlag instance to delete.
        """
        await self.feature_flag_repo.delete_feature_flag(flag)
        await self.session.commit()

    async def get_feature_flags(
            self,
            filters: FeatureFlagFilter,
    ) -> list[FeatureFlag]:
        """Lists feature flags matching the given filters.

        Args:
            filters: FeatureFlagFilter with search, status, and ordering criteria.

        Returns:
            List of matching FeatureFlag instances.
        """
        return await self.feature_flag_repo.get_feature_flags(filters)

    async def get_feature_flag_by_id(
            self,
            flag_id: int,
    ) -> FeatureFlag:
        """Fetches a single feature flag by ID.

        Args:
            flag_id: ID of the feature flag to fetch.

        Returns:
            Matching FeatureFlag instance.

        Raises:
            FeatureFlagNotFoundError: When no feature flag matches the ID.
        """
        result = await self.feature_flag_repo.get_feature_flag_by_id(flag_id)
        if not result:
            raise FeatureFlagNotFoundError("Feature flag not found")
        return result

    async def evaluate_flags_for_user(
            self,
            user: User,
    ) -> dict[str, bool]:
        """Evaluates every enabled feature flag's staged rollout for the given user.

        Args:
            user: User to evaluate flags for.

        Returns:
            Mapping of flag key to whether it is enabled for this user.
        """
        flags = await self.feature_flag_repo.get_enabled_feature_flags()
        return {
            flag.key: _bucket_for(flag.key, user.id) < flag.rollout_percentage
            for flag in flags
        }
