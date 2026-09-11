import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, field_validator

from src.backend.identity.auth.exceptions import InvalidUsernameError
from src.backend.identity.auth.validators import validate_password


class UserRoleEnum(str, Enum):
    """System-level user roles: regular user or admin."""

    user = "user"
    admin = "admin"
    librarian = "librarian"

class Token(BaseModel):
    """Authentication token pair returned after successful login or token refresh."""

    access_token: str
    refresh_token: str
    session_id: int
    token_type: str = "Bearer"

class RefreshToken(BaseModel):
    """Request payload for refreshing the access token using a refresh token."""

    refresh_token: str

class UserBase(BaseModel):
    """Shared user fields with username format validation; base for register and update schemas."""

    username: str = Field(min_length=3, max_length=100)
    email: EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Validates that the username starts with a letter and contains only letters, digits, and underscores.

        Args:
            value: Username string to validate.

        Returns:
            The username lowercased.

        Raises:
            InvalidUsernameError: When the username does not match the required format.
        """
        if not re.fullmatch(r'^[A-Za-z][A-Za-z0-9_]*$', value):
            raise InvalidUsernameError("Username must consist of letters and numbers")
        return value.lower()


class UserRegister(UserBase):
    """Request payload for registering a new user; validates password strength on input."""

    password: str
    fullname: str

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value):
        """Validates the password against strength requirements.

        Args:
            value: Plain-text password to validate.

        Returns:
            The original password string if valid.
        """
        return validate_password(value)

class ChangeUserPassword(BaseModel):
    """Request payload for changing the user's password; validates the new password on input."""

    old_password: str
    new_password: str

    @field_validator("new_password", mode="before")
    @classmethod
    def validate_password(cls, value):
        """Validates the new password against strength requirements.

        Args:
            value: Plain-text password to validate.

        Returns:
            The original password string if valid.
        """
        return validate_password(value)

class ForgotPassword(BaseModel):
    """Request payload for initiating a password reset via email."""

    email: str


class ResetPassword(BaseModel):
    """Request payload for completing a password reset; validates the new password on input."""

    token: str
    new_password: str

    @field_validator("new_password", mode="before")
    @classmethod
    def validate_password(cls, value):
        """Validates the new password against strength requirements.

        Args:
            value: Plain-text password to validate.

        Returns:
            The original password string if valid.
        """
        return validate_password(value)


class UpdateUser(UserBase):
    """Request payload for updating the user's profile fields (username, email, etc.)."""

class TwoFactorRequired(BaseModel):
    """Response returned from login when the account has two-factor authentication enabled."""

    two_factor_required: bool = True
    pre_auth_token: str

class TwoFactorSetup(BaseModel):
    """Response payload with the pending TOTP secret and its provisioning URI."""

    secret: str
    provisioning_uri: str

class TwoFactorEnable(BaseModel):
    """Request payload for confirming a pending TOTP secret and enabling two-factor authentication."""

    code: str

class TwoFactorRecoveryCodes(BaseModel):
    """Response payload with newly generated single-use recovery codes."""

    recovery_codes: list[str]

class TwoFactorDisable(BaseModel):
    """Request payload for disabling two-factor authentication."""

    password: str

class TwoFactorVerify(BaseModel):
    """Request payload for completing a pending login with a TOTP or recovery code."""

    pre_auth_token: str
    code: str

class OAuthProviderEnum(str, Enum):
    """Supported OAuth identity providers for federated sign-in."""

    google = "google"
    apple = "apple"

class OAuthLogin(BaseModel):
    """Request payload for signing in via an OAuth provider's identity token."""

    id_token: str

class GetSession(BaseModel):
    """Response payload describing a user's active session."""

    id: int
    user_id: int
    username: str | None = None
    device_label: str
    ip_address: str
    last_active_at: datetime
    expires_at: datetime