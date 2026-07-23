from datetime import datetime, timezone

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from backend.identity.profile.managers import ProfileManager
from backend.identity.profile.schemas import CreateProfile
from backend.library.shelf.managers.shelf import ShelfManager
from src.backend.identity.auth.exceptions import InvalidUsernameOrPasswordError, UnverifiedUserError, \
    UsernameAlreadyExists, EmailAlreadyExists, InvalidTokenError
from src.backend.identity.auth.models import User
from src.backend.identity.auth.repository import SessionRepository
from src.backend.identity.auth.schemas import Token, UserRegister, ChangeUserPassword, ResetPassword, UpdateUser
from src.backend.identity.auth.services.email import create_verification_token, create_password_reset_token, \
    decode_password_reset_token
from src.backend.identity.auth.services.security import PasswordService, TokenService, hash_token, \
    send_verification_email, send_password_reset_email
from src.backend.identity.users.managers import UserManager
from src.backend.identity.users.repository import UserRepository


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
        self.profile_manager = ProfileManager(session)
        self.user_manager = UserManager(session)
        self.shelf_manager = ShelfManager(session)

    async def login(
            self,
            username: str,
            password: str,
            request
    ) -> Token:
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            raise InvalidUsernameOrPasswordError("Invalid username or password")

        if not user.is_verified:
            raise UnverifiedUserError("Please verify your email before logging in")

        if not self.password_service.verify(password, user.hashed_password):
            raise InvalidUsernameOrPasswordError("Invalid username or password")

        access_token = self.token_service.encode(str(user.id))
        refresh_token = self.token_service.encode(str(user.id), is_refresh=True)

        session = await self.session_repo.create(
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_token),
            device_label=request.headers.get("user-agent", "Unknown device"),
            ip_address=request.client.host
        )

        if user.is_deleted:
            await self.user_repo.update_delete(user,False)

        await self.session.commit()
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session.id
        )

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
        await send_verification_email(user.email, token)

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
        """
        user_username = await self.user_repo.exists_username(request.username, user.id)
        if user_username:
            raise UsernameAlreadyExists("Username already exists")

        user_email = await self.user_repo.exists_email(str(request.email), user.id)
        if user_email:
            raise EmailAlreadyExists("Email already exists")

        await self.user_repo.update(
            user=user,
            username=request.username,
            email=str(request.email),
        )
        await self.session.commit()

    async def forgot_password(
            self,
            user: User
    ):
        if user and user.is_verified:
            token = create_password_reset_token(user)
            await send_password_reset_email(user.email, token)
        return {"Reset link has been sent"}

    async def reset_password(
            self,
            request: ResetPassword
    ):
        user_id = await decode_password_reset_token(request.token, self.user_manager)
        user = await self.user_manager.get_user_by_id(int(user_id))
        await self.set_password(user, request)
        sessions = await self.session_repo.get_user_active_sessions(user.id)
        for s in sessions:
            await self.session_repo.delete(s)
        await self.session.commit()
