import hashlib
from datetime import timedelta, datetime

from jose import jwt, JWTError
from passlib.hash import argon2

from src.backend.core.settings import settings
from src.backend.identity.auth.exceptions import InvalidTokenError


class TokenService:
    """Handles JWT encoding and decoding for access and refresh tokens."""

    def encode(
            self,
            sub: str,
            is_refresh: bool = False
    ):
        """Encodes a JWT with a subject claim and expiry based on token type.

        Args:
            sub: User ID string to embed as the subject claim.
            is_refresh: If True, applies refresh token expiry; otherwise access token expiry.

        Returns:
            Signed JWT string.
        """
        exp = timedelta(minutes=settings.REFRESH_EXPIRES) if is_refresh else timedelta(minutes=settings.ACCESS_EXPIRES)
        payload = {
            "sub": sub,
            "is_refresh": is_refresh,
            "exp": datetime.now() + exp
        }
        return jwt.encode(
            payload,
            algorithm=settings.TOKEN_ALGORITHM,
            key=settings.TOKEN_SECRET_KEY
        )

    def encode_two_factor_pending(
            self,
            sub: str
    ):
        """Encodes a short-lived JWT marking a login as pending two-factor verification.

        Args:
            sub: User ID string to embed as the subject claim.

        Returns:
            Signed JWT string.
        """
        payload = {
            "sub": sub,
            "two_factor_pending": True,
            "exp": datetime.now() + timedelta(minutes=5)
        }
        return jwt.encode(
            payload,
            algorithm=settings.TOKEN_ALGORITHM,
            key=settings.TOKEN_SECRET_KEY
        )

    def decode(
            self,
            token: str
    ) -> dict:
        """Decodes and validates a JWT, returning its payload.

        Args:
            token: Signed JWT string to decode.

        Returns:
            Decoded payload dict.

        Raises:
            InvalidTokenError: When the token is invalid or expired.
        """
        try:
            payload = jwt.decode(
                token,
                algorithms=[settings.TOKEN_ALGORITHM],
                key=settings.TOKEN_SECRET_KEY
            )
        except JWTError:
            raise InvalidTokenError("Неверные учетные данные")
        return payload



class PasswordService:
    """Handles Argon2 password hashing and verification."""

    def hash(
            self,
            password: str
    ) -> str:
        """Hashes a plain-text password using Argon2.

        Args:
            password: Plain-text password string.

        Returns:
            Argon2 hash string.
        """
        return argon2.hash(
            password
        )

    def verify(
            self,
            password: str,
            hashed_password: str
    ) -> bool:
        """Checks whether a plain-text password matches a stored Argon2 hash.

        Args:
            password: Plain-text password to check.
            hashed_password: Stored Argon2 hash to compare against.

        Returns:
            True if the password matches, False otherwise.
        """
        return argon2.verify(
            password,
            hashed_password
        )

def hash_token(token: str) -> str:
    """Hashes a token with SHA-256 for safe storage/comparison.

    Args:
        token: Plain-text token string to hash.

    Returns:
        Hex-encoded SHA-256 digest of the token.
    """
    return hashlib.sha256(token.encode()).hexdigest()
