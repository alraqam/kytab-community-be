from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.storage import StorageService
from src.backend.identity.profile.managers import ProfileManager
from src.backend.identity.profile.schemas import CreateProfile
from src.backend.library.shelf.managers.shelf import ShelfManager
from src.backend.identity.auth.exceptions import InvalidUsernameOrPasswordError, UnverifiedUserError, \
    UsernameAlreadyExists, EmailAlreadyExists, InvalidTokenError, UsernameChangeTooSoonError, \
    InvalidTwoFactorCodeError
from src.backend.identity.auth.managers.two_factor import TwoFactorManager
from src.backend.identity.auth.models import User
from src.backend.identity.auth.repository import SessionRepository
from src.backend.identity.auth.schemas import Token, UserRegister, ChangeUserPassword, ResetPassword, UpdateUser, \
    ForgotPassword, TwoFactorRequired
from src.backend.identity.auth.services.email import create_verification_token, create_password_reset_token, \
    decode_password_reset_token, send_verification_email, send_password_reset_email
from src.backend.identity.auth.services.security import PasswordService, TokenService, hash_token
from src.backend.identity.users.managers import UserManager
from src.backend.identity.users.repository import UserRepository


USERNAME_CHANGE_COOLDOWN_DAYS = 30


class AuthManager:
    """Handles authentication business logic: login, registration, token management."""

    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)
        self.password_service = PasswordService()
        self.token_service = TokenService()
        self.profile_manager = ProfileManager(session, StorageService())
        self.user_manager = UserManager(session)
        self.shelf_manager = ShelfManager(session)
        self.two_factor_manager = TwoFactorManager(session)

    async def _issue_tokens(
            self,
            user: User,
            request
    ) -> Token:
        """Creates a new session and issues an access/refresh token pair for a user.

        Args:
            user: User to issue tokens for.
            request: Incoming Request, used to read the user-agent and client IP for the new session.

        Returns:
            Newly issued access/refresh Token pair with the created session's ID.
        """
        access_token = self.token_service.encode(str(user.id))
        refresh_token = self.token_service.encode(str(user.id), is_refresh=True)

        session = await self.session_repo.create(
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_token),
            device_label=request.headers.get("user-agent", "Unknown device"),
            ip_address=request.client.host
        )

        if user.is_deleted:
            await self.user_repo.update_delete(user, False)

        await self.session.commit()
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session.id
        )

    async def login(
            self,
            username: str,
            password: str,
            request
    ) -> Token | TwoFactorRequired:
        """Authenticates a user by username and password and starts a new session.

        Args:
            username: Username to authenticate.
            password: Plain-text password to verify.
            request: Incoming Request, used to read the user-agent and client IP for the new session.

        Returns:
            Newly issued access/refresh Token pair with the created session's ID, or a
            TwoFactorRequired response when the account has two-factor authentication enabled.

        Raises:
            InvalidUsernameOrPasswordError: When the username does not exist or the password is wrong.
            UnverifiedUserError: When the user's email has not been verified.
        """
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            raise InvalidUsernameOrPasswordError("Invalid username or password")

        if not user.is_verified:
            raise UnverifiedUserError("Please verify your email before logging in")

        if not self.password_service.verify(password, user.hashed_password):
            raise InvalidUsernameOrPasswordError("Invalid username or password")

        if user.is_2fa_enabled:
            pre_auth_token = self.token_service.encode_two_factor_pending(str(user.id))
            return TwoFactorRequired(pre_auth_token=pre_auth_token)

        return await self._issue_tokens(user, request)

    async def verify_two_factor(
            self,
            pre_auth_token: str,
            code: str,
            request
    ) -> Token:
        """Completes a pending login by verifying a TOTP or recovery code.

        Args:
            pre_auth_token: Short-lived token issued by login() when two-factor authentication is required.
            code: TOTP code or recovery code entered by the user.
            request: Incoming Request, used to read the user-agent and client IP for the new session.

        Returns:
            Newly issued access/refresh Token pair with the created session's ID.

        Raises:
            InvalidTokenError: When the token is not a valid pending two-factor token, or the user
                no longer has two-factor authentication enabled.
            InvalidTwoFactorCodeError: When the code does not match.
        """
        payload = self.token_service.decode(pre_auth_token)
        if not payload.get("two_factor_pending"):
            raise InvalidTokenError("Invalid token")

        if not payload.get("sub") or not payload.get("sub").isdigit():
            raise InvalidTokenError("Invalid token")

        user = await self.user_repo.get_user_by_id(int(payload.get("sub")))
        if not user or not user.is_2fa_enabled:
            raise InvalidTokenError("Invalid token")

        if not await self.two_factor_manager.verify_code(user, code):
            raise InvalidTwoFactorCodeError("Invalid two-factor code")

        return await self._issue_tokens(user, request)

    async def register(
            self,
            request: UserRegister
    ) -> User:
        """Creates a new user account after validating uniqueness of username and email.

        Args:
            request: UserRegister payload with credentials and profile data.

        Returns:
            Newly created User instance.

        Raises:
            UsernameAlreadyExists: When the username is already taken.
            EmailAlreadyExists: When the email is already registered.
        """
        user = await self.user_repo.exists_username(request.username)
        if user:
            raise UsernameAlreadyExists("Username already exists")

        user = await self.user_repo.exists_email(str(request.email))
        if user:
            raise EmailAlreadyExists("Email already exists")

        hashed_password = self.password_service.hash(request.password)
        user = await self.user_repo.create(
            hashed_password=hashed_password,
            **request.model_dump(
                exclude={"password", "fullname"}
            )
        )
        token = create_verification_token(user.id)
        send_verification_email.delay(user.email, token)

        profile = await self.profile_manager.create(
            CreateProfile(
                user_id=user.id,
                fullname=request.fullname,
            )
        )
        shelves = await self.shelf_manager.create_default_shelves(user)
        await self.session.commit()
        return user

    async def get_me(
            self,
            token: str
    ) -> User:
        """Resolves the current user from an access token.

        Args:
            token: JWT access token string.

        Returns:
            User instance matching the token subject.

        Raises:
            InvalidTokenError: When the token is a refresh token, malformed, or user not found.
        """
        payload = self.token_service.decode(token)
        if payload.get("is_refresh", True):
            raise InvalidTokenError("Invalid Credentials")

        if not payload.get("sub") or not payload.get("sub").isdigit():
            raise InvalidTokenError("Invalid Credentials")

        user = await self.user_repo.get_user_by_id(int(payload.get("sub")))
        if not user:
            raise InvalidTokenError("Invalid Credentials")

        return user

    async def refresh_token(
            self,
            token: str
    ) -> Token:
        """Issues a new access/refresh token pair from a valid refresh token.

        Args:
            token: Refresh token string to validate and rotate.

        Returns:
            Newly issued access/refresh Token pair with the session's ID.

        Raises:
            InvalidTokenError: When the token is not a refresh token, is malformed, or the
                associated session is missing, revoked, or expired.
        """
        payload = self.token_service.decode(token)
        if not payload.get("is_refresh"):
            raise InvalidTokenError("Invalid token")

        if not payload.get("sub") or not payload.get("sub").isdigit():
            raise InvalidTokenError("Invalid token")

        session = await self.session_repo.get_session_by_hash_token(hash_token(token))
        if session is None or session.revoked_at is not None:
            raise InvalidTokenError("Invalid token")
        if session.expires_at < datetime.now(timezone.utc):
            raise InvalidTokenError("Invalid token")

        access_token = self.token_service.encode(payload.get("sub"))
        refresh_token = self.token_service.encode(payload.get("sub"), True)

        session.refresh_token_hash = hash_token(refresh_token)
        session.last_active_at = datetime.now(timezone.utc)

        await self.session_repo.update(session)
        await self.session.commit()
        return Token(access_token=access_token, refresh_token=refresh_token, session_id=session.id)

    async def logout(
            self,
            token: str
    ) -> None:
        """Revokes the session associated with a refresh token.

        Args:
            token: Refresh token identifying the session to revoke.

        Raises:
            InvalidTokenError: When the token is invalid, not a refresh token, or has no matching session.
        """
        try:
            payload = self.token_service.decode(token)
        except jwt.PyJWTError:
            raise InvalidTokenError("Invalid token")

        if not payload.get("is_refresh"):
            raise InvalidTokenError("Invalid token")

        session = await self.session_repo.get_session_by_hash_token(hash_token(token))
        if session is None:
            raise InvalidTokenError("Invalid token")

        await self.session_repo.delete(session)
        await self.session.commit()


    async def change_password(
            self,
            user: User,
            request: ChangeUserPassword
    ) -> None:
        """Changes the user's password after verifying the old one.

        Args:
            user: Authenticated user changing their password.
            request: ChangeUserPassword payload with old_password and new_password.

        Raises:
            InvalidUsernameOrPasswordError: When the old password does not match.
        """
        if not self.password_service.verify(request.old_password, user.hashed_password):
            raise InvalidUsernameOrPasswordError("Invalid username or password")
        hashed_password = self.password_service.hash(request.new_password)
        await self.user_repo.update_password(
            user,
            hashed_password
        )
        await self.session.commit()


    async def set_password(
            self,
            user: User,
            request: ResetPassword
    ) -> None:
        """Sets a new hashed password for the user without checking the old one.

        Args:
            user: User whose password is being set.
            request: ResetPassword payload containing the new password.
        """
        hashed_password = self.password_service.hash(request.new_password)
        await self.user_repo.update_password(
            user,
            hashed_password
        )

    async def update(
            self,
            user: User,
            request: UpdateUser
    ) -> None:
        """Updates the user's username, fullname, and email.

        Args:
            user: Authenticated user updating their profile.
            request: UpdateUser payload with new username, fullname, and email.

        Raises:
            UsernameAlreadyExists: When the requested username is taken by another user.
            EmailAlreadyExists: When the requested email is taken by another user.
            UsernameChangeTooSoonError: When the username was already changed within the last
                USERNAME_CHANGE_COOLDOWN_DAYS days.
        """
        username_changed_at = user.username_changed_at
        if request.username != user.username:
            if user.username_changed_at is not None:
                cooldown_ends = user.username_changed_at + timedelta(days=USERNAME_CHANGE_COOLDOWN_DAYS)
                if datetime.now(timezone.utc) < cooldown_ends:
                    raise UsernameChangeTooSoonError("Username can only be changed once every 30 days")

            user_username = await self.user_repo.exists_username(request.username, user.id)
            if user_username:
                raise UsernameAlreadyExists("Username already exists")

            username_changed_at = datetime.now(timezone.utc)

        user_email = await self.user_repo.exists_email(str(request.email), user.id)
        if user_email:
            raise EmailAlreadyExists("Email already exists")

        await self.user_repo.update(
            user=user,
            username=request.username,
            email=str(request.email),
            username_changed_at=username_changed_at,
        )
        await self.session.commit()

    async def forgot_password(
            self,
            request: ForgotPassword
    ):
        """Sends a password-reset email if the address belongs to a verified user.

        Args:
            request: ForgotPassword payload containing the account email.

        Returns:
            Confirmation message indicating the reset link has been sent.
        """
        user = await self.user_repo.get_user_by_email(request.email)
        if user and user.is_verified:
            token = create_password_reset_token(user)
            send_password_reset_email.delay(user.email, token)
        return {"Reset link has been sent"}

    async def reset_password(
            self,
            request: ResetPassword
    ):
        """Resets a user's password via a password-reset token and revokes their active sessions.

        Args:
            request: ResetPassword payload containing the reset token and new password.

        Raises:
            InvalidTokenError: When the reset token is invalid or expired.
        """
        user_id = await decode_password_reset_token(request.token, self.user_manager)
        user = await self.user_manager.get_user_by_id(int(user_id))
        await self.set_password(user, request)
        sessions = await self.session_repo.get_user_active_sessions(user.id)
        for s in sessions:
            await self.session_repo.delete(s)
        await self.session.commit()
