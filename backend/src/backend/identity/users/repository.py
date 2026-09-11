from dataclasses import dataclass
from datetime import datetime, timezone

from google.api_core.datetime_helpers import utcnow
from sqlalchemy import select, insert, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User


@dataclass
class UserRepository:
    """Data access layer for User model operations."""

    session: AsyncSession

    async def get_user_by_username(
            self,
            username: str
    ) -> User | None:
        """Fetches a user by username.

        Args:
            username: Username to search for.

        Returns:
            User instance if found, None otherwise.
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_id(
            self,
            user_id: int
    ) -> User | None:
        """Fetches a user by ID.

        Args:
            user_id: ID of the user.

        Returns:
            User instance if found, None otherwise.
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user


    async def get_user_by_email(
            self,
            email: str
    ) -> User | None:
        """Fetches a user by email address.

        Args:
            email: Email address to search for.

        Returns:
            User instance if found, None otherwise.
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def get_all_users(
            self,
            filters
    ) -> list[User]:
        """Returns all users, applying optional filters and sorting.

        Args:
            filters: Filter object with filter/sort methods; can be None.

        Returns:
            List of User instances.
        """
        stmt = select(User)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return users

    async def create(
            self,
            username: str,
            email: str,
            hashed_password: str,
            role: str = "user"
    ) -> User:
        """Creates and persists a new user record.

        Args:
            username: Unique username.
            email: User's email address.
            hashed_password: Pre-hashed password string.
            role: User role; defaults to 'user'.

        Returns:
            Newly created User instance.
        """
        stmt = insert(User).values(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
        ).returning(User)
        result = await self.session.execute(stmt)
        await self.session.flush()
        user = result.scalars().first()
        return user


    async def update_role(
            self,
            user: User,
            role: str
    ) -> None:
        """Updates a user's role and flushes the session.

        Args:
            user: User instance to update.
            role: New role string.
        """
        user.role = role
        self.session.add(user)
        await self.session.flush()

    async def update_password(
            self,
            user: User,
            password_hash: str
    ) -> None:
        """Sets a new hashed password on the user and flushes the session.

        Args:
            user: User instance to update.
            password_hash: New pre-hashed password string.
        """
        user.hashed_password = password_hash
        self.session.add(user)
        await self.session.flush()


    async def update(
            self,
            user: User,
            username: str,
            email: str,
            username_changed_at: datetime | None,
    ) -> None:
        """Updates the user's username and email fields.

        Args:
            user: User instance to update.
            username: New username string.
            email: New email string.
            username_changed_at: Timestamp to record for the username change, or the
                existing value if the username is not being changed.
        """
        user.username = username
        user.email = email
        user.username_changed_at = username_changed_at
        self.session.add(user)
        await self.session.flush()


    async def update_activity(
            self,
            user: User,
            is_active: bool
    ) -> None:
        """Updates a user's active status and flushes the session.

        Args:
            user: User instance to update.
            is_active: New active status boolean.
        """
        user.is_active = is_active
        self.session.add(user)
        await self.session.flush()

    async def update_verification(
            self,
            user: User,
            is_verified: bool
    ) -> None:
        """Updates a user's verification status and flushes the session.

        Args:
            user: User instance to update.
            is_verified: New verification status boolean.
        """
        user.is_verified = is_verified
        self.session.add(user)
        await self.session.flush()

    async def update_delete(
            self,
            user: User,
            is_deleted: bool
    ):
        """Sets a user's deleted flag and deleted timestamp.

        Args:
            user: User instance to update.
            is_deleted: True to mark deleted, False to restore.
        """
        user.is_deleted = is_deleted
        user.deleted_at = datetime.now(timezone.utc) if is_deleted else None
        await self.session.flush()

    async def update_totp_secret(
            self,
            user: User,
            totp_secret: str | None
    ) -> None:
        """Sets or clears the user's pending/active TOTP secret and flushes the session.

        Args:
            user: User instance to update.
            totp_secret: New base32-encoded TOTP secret, or None to clear it.
        """
        user.totp_secret = totp_secret
        self.session.add(user)
        await self.session.flush()

    async def update_2fa_enabled(
            self,
            user: User,
            is_2fa_enabled: bool
    ) -> None:
        """Sets the user's two-factor enabled flag and flushes the session.

        Args:
            user: User instance to update.
            is_2fa_enabled: New two-factor enabled status.
        """
        user.is_2fa_enabled = is_2fa_enabled
        self.session.add(user)
        await self.session.flush()

    async def exists_username(self, username: str, user_id: int = None) -> bool:
        """Checks whether a username is already taken.

        Args:
            username: Username to check.
            user_id: If provided, excludes the user with this ID from the check.

        Returns:
            True if the username exists for another user; False otherwise.
        """
        condition = (User.username == username)
        if user_id:
            condition = condition & (User.id != user_id)
        stmt = select(exists().where(condition))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def exists_email(self, email: str, user_id: int = None) -> bool:
        """Checks whether an email address is already registered.

        Args:
            email: Email address to check.
            user_id: If provided, excludes the user with this ID from the check.

        Returns:
            True if the email exists for another user; False otherwise.
        """
        condition = (User.email == email)
        if user_id:
            condition = condition & (User.id != user_id)
        stmt = select(exists().where(condition))
        result = await self.session.execute(stmt)
        return result.scalar()
