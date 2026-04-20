"""Exception hierarchy for the CuteMarkets client.

Every exception raised by this package inherits from :class:`CuteMarketsError`.
API-returned errors (HTTP != 2xx with the standard envelope) are surfaced as
:class:`APIError` subclasses selected by HTTP status and the ``error.code``
field in the response body. Network/IO issues are wrapped in
:class:`TransportError`.
"""

from __future__ import annotations

from typing import Any, Optional


class CuteMarketsError(Exception):
    """Base class for every exception raised by this library."""


class ConfigurationError(CuteMarketsError):
    """Raised when the client is misconfigured (e.g. missing API key)."""


class TransportError(CuteMarketsError):
    """Raised when the HTTP layer fails (connection error, timeout, ...)."""

    def __init__(self, message: str, *, original: Optional[BaseException] = None) -> None:
        super().__init__(message)
        self.original = original


class APIError(CuteMarketsError):
    """Base class for any non-2xx response from the API.

    Attributes:
        status_code: HTTP status code returned by the API.
        code: Machine-readable ``error.code`` from the response envelope, when present.
        message: Human-readable error message from the response envelope.
        request_id: Unique ``request_id`` assigned by CuteMarkets, useful for support.
        response: The decoded JSON body, if available.
        rate_limit: :class:`~cutemarkets.models.common.RateLimitInfo` parsed from headers.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: Optional[str] = None,
        request_id: Optional[str] = None,
        response: Optional[Any] = None,
        rate_limit: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.request_id = request_id
        self.response = response
        self.rate_limit = rate_limit

    def __str__(self) -> str:
        parts = [f"HTTP {self.status_code}"]
        if self.code:
            parts.append(self.code)
        parts.append(self.message or "")
        tail = f" (request_id={self.request_id})" if self.request_id else ""
        return ": ".join(p for p in parts if p) + tail


class BadRequestError(APIError):
    """HTTP 400 with ``code='bad_request'``: missing or invalid query parameters."""


class InvalidPageTokenError(BadRequestError):
    """HTTP 400 with ``code='invalid_page_token'``.

    The ``page`` parameter is invalid or expired. Repeat the list request
    without ``page``, then follow each ``next_url`` the API returns.
    """


class AuthenticationError(APIError):
    """HTTP 401 with ``code='unauthorized'``: missing or invalid API key."""


class ForbiddenError(APIError):
    """HTTP 403 with ``code='forbidden'``: your plan does not include this endpoint."""


class LookbackExceededError(ForbiddenError):
    """HTTP 403 with ``code='lookback_exceeded'``.

    A date or timestamp parameter falls outside your plan's historical
    lookback window (3 years for Free, 7 years for Developer, 10 years for
    Expert). Upgrade your plan or adjust the date range.
    """


class NotFoundError(APIError):
    """HTTP 404: the requested resource does not exist."""


class RateLimitError(APIError):
    """HTTP 429: you exceeded your plan's request limit."""


_CODE_MAP: dict[str, type[APIError]] = {
    "bad_request": BadRequestError,
    "invalid_page_token": InvalidPageTokenError,
    "unauthorized": AuthenticationError,
    "forbidden": ForbiddenError,
    "lookback_exceeded": LookbackExceededError,
    "not_found": NotFoundError,
    "rate_limit_exceeded": RateLimitError,
}

_STATUS_FALLBACK: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    429: RateLimitError,
}


def error_from_response(
    status_code: int,
    payload: Any,
    *,
    rate_limit: Optional[Any] = None,
) -> APIError:
    """Build the best-fitting :class:`APIError` subclass for a failed response.

    Selection prefers the ``error.code`` value from the response body (so that
    e.g. ``403 lookback_exceeded`` maps to :class:`LookbackExceededError` rather
    than the generic :class:`ForbiddenError`). Falls back to the HTTP status
    code, and finally to the base :class:`APIError`.
    """
    code: Optional[str] = None
    message = ""
    request_id: Optional[str] = None
    if isinstance(payload, dict):
        request_id = payload.get("request_id") if isinstance(payload.get("request_id"), str) else None
        error_obj = payload.get("error")
        if isinstance(error_obj, dict):
            raw_code = error_obj.get("code")
            if isinstance(raw_code, str):
                code = raw_code
            raw_message = error_obj.get("message")
            if isinstance(raw_message, str):
                message = raw_message
    if not message:
        message = f"HTTP {status_code} error"

    exc_cls: type[APIError] = APIError
    if code and code in _CODE_MAP:
        exc_cls = _CODE_MAP[code]
    elif status_code in _STATUS_FALLBACK:
        exc_cls = _STATUS_FALLBACK[status_code]

    return exc_cls(
        message,
        status_code=status_code,
        code=code,
        request_id=request_id,
        response=payload,
        rate_limit=rate_limit,
    )


__all__ = [
    "CuteMarketsError",
    "ConfigurationError",
    "TransportError",
    "APIError",
    "BadRequestError",
    "InvalidPageTokenError",
    "AuthenticationError",
    "ForbiddenError",
    "LookbackExceededError",
    "NotFoundError",
    "RateLimitError",
    "error_from_response",
]
