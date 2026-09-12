import hashlib
import time

import httpx
from jose import jwt
from jose.exceptions import JWTError

from src.backend.core.redis import redis_client
from src.backend.core.settings import settings
from src.backend.identity.auth.exceptions import InvalidOAuthTokenError


class OAuthService:
    """Verifies OAuth identity tokens from Google and Apple against their published JWKS."""

    PROVIDERS = {
        "google": {
            "jwks_url": "https://www.googleapis.com/oauth2/v3/certs",
            "issuers": ("https://accounts.google.com", "accounts.google.com"),
            "audience_setting": "GOOGLE_CLIENT_ID",
        },
        "apple": {
            "jwks_url": "https://appleid.apple.com/auth/keys",
            "issuers": ("https://appleid.apple.com",),
            "audience_setting": "APPLE_CLIENT_ID",
        },
    }

    def __init__(self):
        self._jwks_cache: dict[str, list[dict]] = {}

    async def _fetch_jwks(self, jwks_url: str) -> list[dict]:
        """Downloads the current signing keys published at a provider's JWKS endpoint.

        Args:
            jwks_url: URL of the provider's JWKS endpoint.

        Returns:
            List of JWK dicts.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=5)
            response.raise_for_status()
        return response.json()["keys"]

    async def _get_signing_key(self, jwks_url: str, kid: str | None) -> dict:
        """Resolves the JWK matching a token's key ID, refreshing the cache on a miss.

        Args:
            jwks_url: URL of the provider's JWKS endpoint.
            kid: Key ID from the token's header.

        Returns:
            Matching JWK dict.

        Raises:
            InvalidOAuthTokenError: When no key matches, even after refreshing the cache.
        """
        keys = self._jwks_cache.get(jwks_url) or await self._fetch_jwks(jwks_url)
        key = next((k for k in keys if k.get("kid") == kid), None)
        if key is None:
            keys = await self._fetch_jwks(jwks_url)
            key = next((k for k in keys if k.get("kid") == kid), None)
        self._jwks_cache[jwks_url] = keys
        if key is None:
            raise InvalidOAuthTokenError("Invalid OAuth token")
        return key

    async def verify(self, provider: str, id_token: str) -> dict:
        """Verifies an OAuth identity token's signature, issuer, and audience.

        Args:
            provider: OAuth provider name ("google" or "apple").
            id_token: Signed identity token issued by the provider.

        Returns:
            Decoded token claims (sub, email, email_verified, name, etc.).

        Raises:
            InvalidOAuthTokenError: When the token is malformed, expired, or fails verification.
        """
        config = self.PROVIDERS[provider]
        try:
            header = jwt.get_unverified_header(id_token)
            key = await self._get_signing_key(config["jwks_url"], header.get("kid"))
            claims = jwt.decode(
                id_token,
                key,
                algorithms=["RS256"],
                audience=getattr(settings, config["audience_setting"]),
                options={"verify_iss": False},
            )
        except JWTError:
            raise InvalidOAuthTokenError("Invalid OAuth token")

        if claims.get("iss") not in config["issuers"]:
            raise InvalidOAuthTokenError("Invalid OAuth token")

        replay_key = f"oauth:used_token:{provider}:{hashlib.sha256(id_token.encode()).hexdigest()}"
        ttl = max(int(claims["exp"] - time.time()), 1)
        if not await redis_client.set(replay_key, "1", nx=True, ex=ttl):
            raise InvalidOAuthTokenError("Invalid OAuth token")

        return claims
