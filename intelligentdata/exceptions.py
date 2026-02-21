"""Exceptions for the Intelligent Data API SDK."""


class ApiError(Exception):
    """Raised when the API returns a non-success response."""

    def __init__(self, status_code: int, message: str, raw: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.raw = raw or {}
        super().__init__(f"[{status_code}] {message}")


class AuthenticationError(ApiError):
    """Raised on 401/403 responses."""

    def __init__(self, message: str = "Authentication failed", raw: dict | None = None):
        super().__init__(401, message, raw)


class RateLimitError(ApiError):
    """Raised on 429 responses."""

    def __init__(self, retry_after: float | None = None, raw: dict | None = None):
        self.retry_after = retry_after
        super().__init__(429, "Rate limit exceeded", raw)
