# Intelligent Data API — Python SDK

Python client for the [Intelligent Data API](https://portal.smartvmapi.com) by apexanalytix. Validate addresses, tax IDs, and bank accounts; look up business registrations; screen for sanctions and disqualified directors.

## Installation

```bash
pip install intelligentdata
```

## Quick Start

```python
from intelligentdata import IntelligentDataClient, AddressRequest

client = IntelligentDataClient(api_key="svm...")

result = client.validate_address(AddressRequest(
    address_line1="123 Main St",
    city="New York",
    state="NY",
    postal_code="10001",
    country="US",
))
print(f"Valid: {result.is_valid}, Score: {result.confidence_score}")
```

## Authentication

### API Key (recommended)

```python
client = IntelligentDataClient(api_key="svm...")
```

### OAuth2 Client Credentials

```python
client = IntelligentDataClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

## Methods

| Method | Description | Endpoint |
|--------|-------------|----------|
| `validate_address()` | Validate and standardize a postal address | POST /api/validate/address |
| `validate_tax_id()` | Validate a tax identification number | POST /api/validate/taxid |
| `validate_bank_account()` | Verify bank account details | POST /api/validate/bank |
| `lookup_business()` | Look up official business registration data | POST /api/enrich/business |
| `check_sanctions()` | Screen against global sanctions lists | POST /api/risk/sanctions |
| `check_directors()` | Check for disqualified directors | POST /api/risk/directors |

## Error Handling

```python
from intelligentdata import IntelligentDataClient, ApiError, RateLimitError

client = IntelligentDataClient(api_key="svm...")

try:
    result = client.validate_address(req)
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ApiError as e:
    print(f"API error [{e.status_code}]: {e.message}")
```

All response objects include a `raw` dict with the full API response for fields not yet mapped to typed properties.

## Context Manager

```python
with IntelligentDataClient(api_key="svm...") as client:
    result = client.validate_address(req)
```

## Configuration

```python
client = IntelligentDataClient(
    api_key="svm...",
    base_url="https://api.smartvmapi.com",  # default
    timeout=30.0,                            # seconds
)
```

## Requirements

- Python 3.9+
- httpx

## License

MIT
