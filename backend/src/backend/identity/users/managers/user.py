from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.services.assignment import ClubAssignmentService
from src.backend.identity.auth.models.auth import User
from src.backend.identity.auth.schemas.auth import UserRoleEnum
from src.backend.identity.auth.repository.session import SessionRepository
from src.backend.identity.users.exceptions.user import UserNotFoundError
from src.backend.identity.users.filters.user import UserFilter
from src.backend.identity.users.repository.user import UserRepository
from src.backend.identity.users.schemas.user import UpdateUserRole, UpdateUserActivity, UpdateUserVerification


class UserManager:
    """Handles business logic for user management operations."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)
        self.club_assignment = ClubAssignmentService(session)

    @staticmethod
    def _is_eligible_manager(role: str, is_active: bool, is_deleted: bool) -> bool:
        """Returns whether a user with these attributes can be assigned clubs as a platform moderator."""
        return role == UserRoleEnum.moderator and bool(is_active) and not is_deleted

    async def _sync_club_assignments(self, user: User, was_eligible: bool) -> None:
        """Rebalances club assignments after a user gains or loses platform-moderator eligibility.

        Losing eligibility (demoted, deactivated, deleted) hands the user's active clubs to the
        remaining moderators. Gaining it picks up any clubs left without a moderator.

        Args:
            user: User whose role, activity, or deletion status just changed (already flushed).
            was_eligible: Whether the user was an eligible platform moderator before the change.
        """
        is_eligible = self._is_eligible_manager(user.role, user.is_active, user.is_deleted)
        if was_eligible and not is_eligible:
            await self.club_assignment.reassign_all_from(user)
        elif is_eligible and not was_eligible:
            await self.club_assignment.assign_unassigned()

    async def update_user_role(
            self,
            user: User,
            request: UpdateUserRole,
    ) -> None:
        """Updates the role of the given user and rebalances club assignments if they gained or lost the moderator role.

        Args:
            user: User instance to update.
            request: UpdateUserRole schema with the new role value.
        """
        was_eligible = self._is_eligible_manager(user.role, user.is_active, user.is_deleted)
        await self.user_repo.update_role(
            user=user,
            role=request.role
        )
        await self._sync_club_assignments(user, was_eligible)
        await self.session.commit()

    async def update_user_activity(
            self,
            user: User,
            request: UpdateUserActivity
    ) -> None:
        """Updates the active status of the given user and rebalances club assignments for platform moderators.

        Args:
            user: User instance to update.
            request: UpdateUserActivity schema with the new is_active value.
        """
        was_eligible = self._is_eligible_manager(user.role, user.is_active, user.is_deleted)
        await self.user_repo.update_activity(
            user=user,
            is_active=request.is_active
        )
        await self._sync_club_assignments(user, was_eligible)
        await self.session.commit()

    async def update_verification(
            self,
            user_id: int,
            request: UpdateUserVerification
    ) -> None:
        """Updates the verification status of a user resolved by ID.

        Args:
            user_id: ID of the user to update.
            request: UpdateUserVerification schema with the new is_verified value.

        Raises:
            UserNotFoundError: When no user with the given ID exists.
        """
        user = await self.get_user_by_id(user_id)
        await self.user_repo.update_verification(
            user=user,
            is_verified=request.is_verified
        )
        await self.session.commit()

    async def get_user_by_id(
            self,
            user_id: int,
    ) -> User:
        """Fetches a user by ID, raising an error if not found.

        Args:
            user_id: ID of the user to retrieve.

        Returns:
            User instance.

        Raises:
            UserNotFoundError: When no user with the given ID exists.
        """
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        return user

    async def get_user_by_email(
            self,
            email: str,
    ) -> User:
        """Fetches a user by email, raising an error if not found.

        Args:
            email: Email address of the user to retrieve.

        Returns:
            User instance.

        Raises:
            UserNotFoundError: When no user with the given email exists.
        """
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")
        return user

    async def get_user_by_username(
            self,
            username: str,
    ) -> User | None:
        """Fetches a user by username.

        Args:
            username: Username of the user to retrieve.

        Returns:
            User instance if found, None otherwise.
        """
        return await self.user_repo.get_user_by_username(username)

    async def get_all_users(
            self,
            filters: UserFilter
    ) -> list[User]:
        """Returns all users matching the given filters.

        Args:
            filters: UserFilter instance with optional filter and sort parameters.

        Returns:
            List of User instances.
        """
        users = await self.user_repo.get_all_users(filters)
        return users


    async def delete_user(
            self,
            user: User,
    ) -> None:
        """Soft-deletes a user, revokes all of their active sessions, and hands a platform moderator's clubs to the others.

        Args:
            user: User instance to delete.
        """
        was_eligible = self._is_eligible_manager(user.role, user.is_active, user.is_deleted)
        sessions = await self.session_repo.get_user_active_sessions(user.id)
        for session in sessions:
            await self.session_repo.delete(session)
        await self.user_repo.update_delete(user, True)
        await self._sync_club_assignments(user, was_eligible)
        await self.session.commit()