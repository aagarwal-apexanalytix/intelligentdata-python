"""Intelligent Data API client."""

from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any, TypeVar

import httpx

from .auth import OAuth2TokenManager
from .exceptions import ApiError, AuthenticationError, RateLimitError
from .models import (
    AddressRequest,
    AddressResponse,
    BankAccountRequest,
    BankAccountResponse,
    BusinessLookupRequest,
    BusinessLookupResponse,
    DirectorsRequest,
    DirectorsResponse,
    SanctionsRequest,
    SanctionsResponse,
    TaxIdRequest,
    TaxIdResponse,
)

T = TypeVar("T")

_VERSION = "0.1.0"
_DEFAULT_BASE_URL = "https://api.smartvmapi.com"
_MAX_RETRIES = 3


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])


def _serialize(obj: Any) -> dict[str, Any]:
    raw = asdict(obj)
    return {_to_camel(k): v for k, v in raw.items() if v != "" and v != 0}


class IntelligentDataClient:
    """Client for the Intelligent Data API.

    Supports API key authentication (primary) and OAuth2 client credentials.

    Usage::

        client = IntelligentDataClient(api_key="svm...")
        result = client.validate_address(AddressRequest(
            address_line1="123 Main St", city="New York",
            state="NY", postal_code="10001", country="US",
        ))
    """

    def __init__(
        self,
        api_key: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        token_url: str | None = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": f"intelligentdata-python-sdk/{_VERSION}"},
        )
        self._oauth: OAuth2TokenManager | None = None
        if client_id and client_secret:
            self._oauth = OAuth2TokenManager(
                client_id=client_id,
                client_secret=client_secret,
                token_url=token_url or f"{self._base_url}/api/oauth/token",
                http_client=self._http,
            )

    def __enter__(self) -> IntelligentDataClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key
        elif self._oauth:
            headers["Authorization"] = f"Bearer {self._oauth.get_token()}"
        return headers

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        last_err: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._http.request(
                    method,
                    url,
                    json=body,
                    headers=self._headers(),
                )
            except httpx.TransportError as exc:
                last_err = exc
                time.sleep(2**attempt)
                continue

            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", 2**attempt))
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(retry_after)
                    continue
                raise RateLimitError(retry_after=retry_after, raw=resp.json() if resp.content else None)

            if resp.status_code >= 500:
                last_err = ApiError(resp.status_code, resp.text)
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(2**attempt)
                    continue
                raise last_err

            if resp.status_code in (401, 403):
                data = resp.json() if resp.content else {}
                raise AuthenticationError(data.get("message", "Authentication failed"), raw=data)

            if resp.status_code >= 400:
                data = resp.json() if resp.content else {}
                raise ApiError(resp.status_code, data.get("message", "Request failed"), raw=data)

            return resp.json()

        raise last_err or ApiError(0, "Request failed after retries")

    # ── Public Methods ────────────────────────────────────────────────────

    def validate_address(self, req: AddressRequest) -> AddressResponse:
        """Validate and standardize a postal address."""
        data = self._request("POST", "/api/validate/address", _serialize(req))
        return AddressResponse(
            is_valid=data.get("isValid", False),
            confidence_score=data.get("confidenceScore", 0.0),
            standardized_address=data.get("standardizedAddress", {}),
            raw=data,
        )

    def validate_tax_id(self, req: TaxIdRequest) -> TaxIdResponse:
        """Validate a tax identification number."""
        data = self._request("POST", "/api/validate/taxid", _serialize(req))
        return TaxIdResponse(
            is_valid=data.get("isValid", False),
            tax_id_type=data.get("taxIdType", ""),
            country=data.get("country", ""),
            registered_name=data.get("registeredName", ""),
            raw=data,
        )

    def validate_bank_account(self, req: BankAccountRequest) -> BankAccountResponse:
        """Verify bank account details."""
        data = self._request("POST", "/api/validate/bank", _serialize(req))
        return BankAccountResponse(
            is_valid=data.get("isValid", False),
            bank_name=data.get("bankName", ""),
            account_type=data.get("accountType", ""),
            raw=data,
        )

    def lookup_business(self, req: BusinessLookupRequest) -> BusinessLookupResponse:
        """Look up official business registration data."""
        data = self._request("POST", "/api/enrich/business", _serialize(req))
        return BusinessLookupResponse(
            found=data.get("found", False),
            company_name=data.get("companyName", ""),
            registration_number=data.get("registrationNumber", ""),
            status=data.get("status", ""),
            address=data.get("address", {}),
            raw=data,
        )

    def check_sanctions(self, req: SanctionsRequest) -> SanctionsResponse:
        """Screen an entity against global sanctions lists."""
        data = self._request("POST", "/api/risk/sanctions", _serialize(req))
        return SanctionsResponse(
            has_matches=data.get("hasMatches", False),
            matches=data.get("matches", []),
            screened_lists=data.get("screenedLists", []),
            raw=data,
        )

    def check_directors(self, req: DirectorsRequest) -> DirectorsResponse:
        """Check for disqualified directors."""
        data = self._request("POST", "/api/risk/directors", _serialize(req))
        return DirectorsResponse(
            has_disqualified=data.get("hasDisqualified", False),
            directors=data.get("directors", []),
            raw=data,
        )
