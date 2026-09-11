from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from jose.exceptions import ExpiredSignatureError, JWTError

from src.backend.core.rate_limit import RateLimiter
from src.backend.identity.auth.dependencies import get_auth_manager, get_current_user
from src.backend.identity.auth.exceptions import InvalidTokenError, LinkExpiredError, InvalidUsernameOrPasswordError, \
    UnverifiedUserError, UsernameAlreadyExists, EmailAlreadyExists, InvalidOAuthTokenError, OAuthEmailNotVerifiedError
from src.backend.identity.auth.managers.auth import AuthManager
from src.backend.identity.auth.models import User
from src.backend.identity.auth.schemas import UserRegister, ChangeUserPassword, ResetPassword, UpdateUser, RefreshToken, \
    ForgotPassword, OAuthProviderEnum, OAuthLogin
from src.backend.identity.auth.services.email import decode_verification_token
from src.backend.identity.users.dependencies import get_user_manager

from src.backend.identity.users.managers import UserManager
from src.backend.identity.users.schemas import UpdateUserVerification

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

login_limiter = RateLimiter("login")
register_limiter = RateLimiter("register")
forgot_password_limiter = RateLimiter("forgot-password")
reset_password_limiter = RateLimiter("reset-password")
oauth_login_limiter = RateLimiter("oauth-login")

@cbv(router)
class AuthRouter:
    """CBV router for authentication endpoints: login, register, me, and token refresh."""

    manager: AuthManager = Depends(get_auth_manager)
    user_manager: UserManager = Depends(get_user_manager)

    @router.post(
        "/login",
        summary="authorization to the system"
    )
    async def login(
            self,
            request: Request,
            form_data: OAuth2PasswordRequestForm = Depends()
    ):
        """Authenticates a user and returns an access/refresh token pair."""
        rate_limit_key = f"{request.client.host}:{form_data.username}"
        await login_limiter.check(rate_limit_key)
        try:
            response = await self.manager.login(form_data.username, form_data.password, request)
        except (InvalidUsernameOrPasswordError, UnverifiedUserError):
            await login_limiter.record_failure(rate_limit_key)
            raise
        await login_limiter.reset(rate_limit_key)
        return response

    @router.post(
        "/oauth/{provider}",
        summary="signing in via an OAuth provider"
    )
    async def oauth_login(
            self,
            provider: OAuthProviderEnum,
            payload: OAuthLogin,
            request: Request
    ):
        """Signs a user in via a Google or Apple identity token, linking or creating an account."""
        rate_limit_key = f"{request.client.host}:{provider.value}"
        await oauth_login_limiter.check(rate_limit_key)
        try:
            response = await self.manager.oauth_login(provider.value, payload.id_token, request)
        except (InvalidOAuthTokenError, OAuthEmailNotVerifiedError):
            await oauth_login_limiter.record_failure(rate_limit_key)
            raise
        await oauth_login_limiter.reset(rate_limit_key)
        return response

    @router.post(
        "/register",
        summary="user registration"
    )
    async def register(
            self,
            request: Request,
            payload: UserRegister
    ):
        """Registers a new user account."""
        await register_limiter.check(request.client.host)
        try:
            response = await self.manager.register(payload)
        except (UsernameAlreadyExists, EmailAlreadyExists):
            await register_limiter.record_failure(request.client.host)
            raise
        await register_limiter.reset(request.client.host)
        return response

    @router.post(
        "/logout",
        summary = "logging out from the system"
    )
    async def logout_route(
            self,
            request: RefreshToken,
    ):
        """Logs the user out by revoking the session tied to the given refresh token."""
        await self.manager.logout(request.refresh_token)


    @router.get(
        "/verify-email",
        summary="verifying email")
    async def verify_email(
            self,
            token: str
    ):
        """Verifies a user's email address using a verification token."""
        try:
            user_id = decode_verification_token(token)
        except ExpiredSignatureError:
            raise LinkExpiredError("Verification link expired")
        except JWTError:
            raise InvalidTokenError(400, "Invalid verification token")

        await self.user_manager.update_verification(
            user_id,
            UpdateUserVerification(is_verified=True)
        )
        return {"message": "Email verified"}

    @router.get(
        "/me",
        summary="getting current user"
    )
    async def get_me(
            self,
            user: User = Depends(get_current_user)
    ):
        """Returns the profile of the currently authenticated user."""
        return user

    @router.post(
        "/refresh",
        summary="refresh token",
    )
    async def refresh(
            self,
            request: RefreshToken
    ):
        """Issues a new token pair using the provided refresh token."""
        response = await self.manager.refresh_token(request.refresh_token)
        return response

    @router.delete(
        "/delete",
        summary="delete account",
    )
    async def delete_user(
            self,
            user: User = Depends(get_current_user)
    ):
        """Deletes the currently authenticated user's account."""
        await self.user_manager.delete_user(user)
        return user

    @router.put(
        "/password",
        summary="updating password"
    )
    async def change_password(
            self,
            request: ChangeUserPassword,
            user: User = Depends(get_current_user)
    ) -> None:
        """Changes the current user's password."""
        await self.manager.change_password(user, request)

    @router.put(
        "/info",
        summary="updating current user information"
    )
    async def update_user(
            self,
            request: UpdateUser,
            user: User = Depends(get_current_user)
    ) -> None:
        """Updates the current user's username, fullname, and email."""
        await self.manager.update(user, request)

    @router.post(
        "/forgot-password",
        summary="sending email for resetting password"
    )
    async def forgot_password(
            self,
            request: Request,
            payload: ForgotPassword
    ):
        """Sends a password-reset email to the given address if it belongs to a verified user."""
        await forgot_password_limiter.check(request.client.host)
        result = await self.manager.forgot_password(payload)
        await forgot_password_limiter.record_failure(request.client.host)
        return result

    @router.post(
        "/reset-password",
        summary="resetting password"
    )
    async def reset_password(
            self,
            request: Request,
            payload: ResetPassword
    ):
        """Resets the user's password using a password-reset token."""
        await reset_password_limiter.check(request.client.host)
        try:
            await self.manager.reset_password(payload)
        except InvalidTokenError:
            await reset_password_limiter.record_failure(request.client.host)
            raise
        await reset_password_limiter.reset(request.client.host)