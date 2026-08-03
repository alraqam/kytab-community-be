from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.auth.repository import SessionRepository
from src.backend.identity.users.exceptions import UserNotFoundError
from src.backend.identity.users.filters import UserFilter
from src.backend.identity.users.repository import UserRepository
from src.backend.identity.users.schemas import UpdateUserRole, UpdateUserActivity, UpdateUserVerification


class UserManager:
    """Handles business logic for user management operations."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)

    async def update_user_role(
            self,
            user: User,
            request: UpdateUserRole,
    ) -> None:
        """Updates the role of the given user.

        Args:
            user: User instance to update.
            request: UpdateUserRole schema with the new role value.
        """
        await self.user_repo.update_role(
            user=user,
            role=request.role
        )
        await self.session.commit()

    async def update_user_activity(
            self,
            user: User,
            request: UpdateUserActivity
    ) -> None:
        """Updates the active status of the given user.

        Args:
            user: User instance to update.
            request: UpdateUserActivity schema with the new is_active value.
        """
        await self.user_repo.update_activity(
            user=user,
            is_active=request.is_active
        )
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
        """Soft-deletes a user and revokes all of their active sessions.

        Args:
            user: User instance to delete.
        """
        sessions = await self.session_repo.get_user_active_sessions(user.id)
        for session in sessions:
            await self.session_repo.delete(session)
        await self.user_repo.update_delete(user, True)
        await self.session.commit()