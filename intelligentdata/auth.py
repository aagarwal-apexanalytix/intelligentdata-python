"""OAuth2 token manager for client credentials flow."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx


@dataclass
class _TokenCache:
    access_token: str
    expires_at: float


class OAuth2TokenManager:
    """Manages OAuth2 client credentials tokens with automatic refresh."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        http_client: httpx.Client,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._http_client = http_client
        self._cache: _TokenCache | None = None

    def get_token(self) -> str:
        """Return a valid access token, refreshing if needed."""
        if self._cache and time.time() < self._cache.expires_at - 30:
            return self._cache.access_token

        resp = self._http_client.post(
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        self._cache = _TokenCache(
            access_token=data["access_token"],
            expires_at=time.time() + data.get("expires_in", 3600),
        )
        return self._cache.access_token
