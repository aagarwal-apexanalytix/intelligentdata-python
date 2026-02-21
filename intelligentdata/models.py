"""Request and response models for the Intelligent Data API SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Address Validation ────────────────────────────────────────────────────


@dataclass
class AddressRequest:
    address_line1: str
    city: str
    country: str
    address_line2: str = ""
    state: str = ""
    postal_code: str = ""


@dataclass
class AddressResponse:
    is_valid: bool = False
    confidence_score: float = 0.0
    standardized_address: dict[str, str] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


# ── Tax ID Validation ─────────────────────────────────────────────────────


@dataclass
class TaxIdRequest:
    tax_id: str
    country: str
    tax_id_type: str = ""


@dataclass
class TaxIdResponse:
    is_valid: bool = False
    tax_id_type: str = ""
    country: str = ""
    registered_name: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


# ── Bank Account Validation ───────────────────────────────────────────────


@dataclass
class BankAccountRequest:
    account_number: str
    country: str
    routing_number: str = ""
    iban: str = ""
    bank_code: str = ""


@dataclass
class BankAccountResponse:
    is_valid: bool = False
    bank_name: str = ""
    account_type: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


# ── Business Lookup ───────────────────────────────────────────────────────


@dataclass
class BusinessLookupRequest:
    company_name: str
    country: str
    registration_number: str = ""
    state: str = ""


@dataclass
class BusinessLookupResponse:
    found: bool = False
    company_name: str = ""
    registration_number: str = ""
    status: str = ""
    address: dict[str, str] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


# ── Sanctions Screening ──────────────────────────────────────────────────


@dataclass
class SanctionsRequest:
    entity_name: str
    entity_type: str = "organization"
    country: str = ""


@dataclass
class SanctionsResponse:
    has_matches: bool = False
    matches: list[dict[str, Any]] = field(default_factory=list)
    screened_lists: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


# ── Directors Check ───────────────────────────────────────────────────────


@dataclass
class DirectorsRequest:
    company_name: str
    country: str
    registration_number: str = ""


@dataclass
class DirectorsResponse:
    has_disqualified: bool = False
    directors: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
