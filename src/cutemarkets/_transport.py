"""Low-level HTTP transport shared by the sync and async clients.

Responsibilities:

* Resolve the API key (explicit → env var → unset).
* Serialize query parameters (``date`` / ``datetime`` / ``bool`` / ``Enum``
  coercion, ``_gte/_gt/_lte/_lt`` suffix rewriting to dotted form).
* Send requests with ``httpx``, apply exponential-backoff retries on
  transient failures (network errors, 429, 5xx), and parse the standard
  response envelope.
* Parse rate-limit headers into :class:`RateLimitInfo` and attach it to
  every response (successful or not).
* Raise the best-fitting :class:`APIError` subclass for non-2xx responses.

The public clients (:class:`cutemarkets.CuteMarkets` and
:class:`cutemarkets.AsyncCuteMarkets`) delegate all I/O to the transport
classes defined here.
"""

from __future__ import annotations

import datetime as _dt
import os
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

import httpx

from ._version import __version__
from .errors import ConfigurationError, TransportError, error_from_response
from .models.common import RateLimitInfo

DEFAULT_BASE_URL = "https://api.cutemarkets.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
_RANGE_SUFFIXES = ("_gte", "_gt", "_lte", "_lt")
_USER_AGENT = f"cutemarkets-python/{__version__}"

QueryValue = Union[str, int, float, bool, _dt.date, _dt.datetime, Enum, None, Iterable[Any]]


@dataclass
class Response:
    """Internal representation of a parsed HTTP response.

    ``data`` is ``None`` on 204 No Content (CuteMarkets does not currently
    use 204, but we are defensive). For normal envelope responses, ``data``
    is the decoded JSON body.
    """

    status_code: int
    headers: Mapping[str, str]
    data: Any
    rate_limit: RateLimitInfo
    request_id: Optional[str] = None
    url: str = ""


@dataclass
class ClientOptions:
    """User-facing options for :class:`cutemarkets.CuteMarkets`."""

    api_key: Optional[str] = None
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    user_agent: str = _USER_AGENT
    headers: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Param + URL serialization helpers (shared by sync and async transports)
# ---------------------------------------------------------------------------


def _coerce_value(value: Any) -> Any:
    """Coerce a single query-parameter value into a wire-friendly form."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, _dt.datetime):
        return value.date().isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    if isinstance(value, Enum):
        return _coerce_value(value.value)
    if isinstance(value, (list, tuple)):
        return [_coerce_value(v) for v in value]
    return value


def _rewrite_range_key(key: str) -> str:
    """Rewrite a Pythonic range-filter key to the dotted form the API uses.

    ``strike_price_gte`` → ``strike_price.gte``. Keys that do not end in one
    of the known suffixes are returned unchanged.
    """
    for suffix in _RANGE_SUFFIXES:
        if key.endswith(suffix) and len(key) > len(suffix):
            return key[: -len(suffix)] + "." + suffix[1:]
    return key


def serialize_params(
    params: Optional[Mapping[str, QueryValue]],
) -> List[Tuple[str, str]]:
    """Serialize a dict of user-supplied params into a flat list of tuples.

    * ``None`` values are dropped (so callers can write ``adjusted=None`` to
      mean "use server default").
    * Range filters expressed as ``..._gte`` / ``..._gt`` / ``..._lte`` /
      ``..._lt`` are rewritten to the dotted wire names (``strike_price.gte``).
    * List/tuple values are emitted as multiple ``key=value`` pairs.
    """
    if not params:
        return []
    out: List[Tuple[str, str]] = []
    for raw_key, raw_value in params.items():
        if raw_value is None:
            continue
        key = _rewrite_range_key(raw_key)
        value = _coerce_value(raw_value)
        if isinstance(value, (list, tuple)):
            for item in value:
                if item is None:
                    continue
                out.append((key, str(item)))
        else:
            out.append((key, str(value)))
    return out


def build_url(base_url: str, path: str) -> str:
    """Join a base URL and a path segment without double-slashing."""
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def resolve_api_key(explicit: Optional[str]) -> Optional[str]:
    """Explicit > ``CUTEMARKETS_API_KEY`` env var > ``None``."""
    if explicit:
        return explicit
    env = os.environ.get("CUTEMARKETS_API_KEY")
    return env or None


def build_auth_headers(api_key: Optional[str], user_agent: str) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": user_agent,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def require_api_key(api_key: Optional[str]) -> str:
    if not api_key:
        raise ConfigurationError(
            "No API key configured. Pass api_key=..., call set_api_key(...), "
            "or set the CUTEMARKETS_API_KEY environment variable."
        )
    return api_key


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


def _parse_response(response: httpx.Response) -> Response:
    rate_limit = RateLimitInfo.from_headers(response.headers)
    content_type = response.headers.get("content-type", "")
    data: Any
    if response.status_code == 204 or not response.content:
        data = None
    elif "application/json" in content_type:
        try:
            data = response.json()
        except ValueError:
            data = {"_raw_text": response.text}
    else:
        data = {"_raw_text": response.text}

    request_id: Optional[str] = None
    if isinstance(data, dict):
        raw_id = data.get("request_id")
        if isinstance(raw_id, str):
            request_id = raw_id

    parsed = Response(
        status_code=response.status_code,
        headers=response.headers,
        data=data,
        rate_limit=rate_limit,
        request_id=request_id,
        url=str(response.url),
    )

    if response.status_code >= 400:
        raise error_from_response(
            response.status_code,
            data,
            rate_limit=rate_limit,
        )
    return parsed


def _should_retry_status(status_code: int) -> bool:
    return status_code == 429 or 500 <= status_code < 600


def _retry_sleep(attempt: int) -> float:
    base = min(2.0**attempt, 30.0)
    return base + random.uniform(0, 0.25)


# ---------------------------------------------------------------------------
# Sync transport
# ---------------------------------------------------------------------------


class Transport:
    """Synchronous HTTP transport wrapping :class:`httpx.Client`."""

    def __init__(
        self,
        options: ClientOptions,
        *,
        httpx_transport: Optional[httpx.BaseTransport] = None,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self._options = options
        self._owns_client = client is None
        if client is not None:
            self._client = client
        else:
            self._client = httpx.Client(
                base_url=options.base_url,
                timeout=options.timeout,
                transport=httpx_transport,
            )

    @property
    def options(self) -> ClientOptions:
        return self._options

    @property
    def api_key(self) -> Optional[str]:
        return self._options.api_key

    def set_api_key(self, api_key: Optional[str]) -> None:
        self._options.api_key = api_key

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "Transport":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ---------------- request helpers ----------------

    def _headers(self, *, require_auth: bool) -> Dict[str, str]:
        api_key = self._options.api_key
        if require_auth:
            require_api_key(api_key)
        headers = build_auth_headers(api_key, self._options.user_agent)
        headers.update(self._options.headers)
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, QueryValue]] = None,
        require_auth: bool = True,
    ) -> Response:
        """Send a request by path (prefixed with the configured base URL)."""
        url = build_url(self._options.base_url, path)
        return self._send(
            method,
            url,
            params=serialize_params(params),
            require_auth=require_auth,
        )

    def request_url(
        self,
        method: str,
        url: str,
        *,
        require_auth: bool = True,
    ) -> Response:
        """Send a request to a fully-qualified URL (used for ``next_url``)."""
        return self._send(method, url, params=None, require_auth=require_auth)

    def _send(
        self,
        method: str,
        url: str,
        *,
        params: Optional[List[Tuple[str, str]]],
        require_auth: bool,
    ) -> Response:
        headers = self._headers(require_auth=require_auth)
        attempt = 0
        while True:
            try:
                response = self._client.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                if attempt < self._options.max_retries:
                    time.sleep(_retry_sleep(attempt))
                    attempt += 1
                    continue
                raise TransportError(f"Request timed out: {exc}", original=exc) from exc
            except httpx.HTTPError as exc:
                if attempt < self._options.max_retries:
                    time.sleep(_retry_sleep(attempt))
                    attempt += 1
                    continue
                raise TransportError(f"Network error: {exc}", original=exc) from exc

            if _should_retry_status(response.status_code) and attempt < self._options.max_retries:
                time.sleep(_retry_sleep(attempt))
                attempt += 1
                continue

            return _parse_response(response)


# ---------------------------------------------------------------------------
# Async transport
# ---------------------------------------------------------------------------


class AsyncTransport:
    """Asynchronous HTTP transport wrapping :class:`httpx.AsyncClient`."""

    def __init__(
        self,
        options: ClientOptions,
        *,
        httpx_transport: Optional[httpx.AsyncBaseTransport] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._options = options
        self._owns_client = client is None
        if client is not None:
            self._client = client
        else:
            self._client = httpx.AsyncClient(
                base_url=options.base_url,
                timeout=options.timeout,
                transport=httpx_transport,
            )

    @property
    def options(self) -> ClientOptions:
        return self._options

    @property
    def api_key(self) -> Optional[str]:
        return self._options.api_key

    def set_api_key(self, api_key: Optional[str]) -> None:
        self._options.api_key = api_key

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncTransport":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    def _headers(self, *, require_auth: bool) -> Dict[str, str]:
        api_key = self._options.api_key
        if require_auth:
            require_api_key(api_key)
        headers = build_auth_headers(api_key, self._options.user_agent)
        headers.update(self._options.headers)
        return headers

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, QueryValue]] = None,
        require_auth: bool = True,
    ) -> Response:
        url = build_url(self._options.base_url, path)
        return await self._send(
            method,
            url,
            params=serialize_params(params),
            require_auth=require_auth,
        )

    async def request_url(
        self,
        method: str,
        url: str,
        *,
        require_auth: bool = True,
    ) -> Response:
        return await self._send(method, url, params=None, require_auth=require_auth)

    async def _send(
        self,
        method: str,
        url: str,
        *,
        params: Optional[List[Tuple[str, str]]],
        require_auth: bool,
    ) -> Response:
        import asyncio  # local import: no hard asyncio dep for sync users

        headers = self._headers(require_auth=require_auth)
        attempt = 0
        while True:
            try:
                response = await self._client.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                if attempt < self._options.max_retries:
                    await asyncio.sleep(_retry_sleep(attempt))
                    attempt += 1
                    continue
                raise TransportError(f"Request timed out: {exc}", original=exc) from exc
            except httpx.HTTPError as exc:
                if attempt < self._options.max_retries:
                    await asyncio.sleep(_retry_sleep(attempt))
                    attempt += 1
                    continue
                raise TransportError(f"Network error: {exc}", original=exc) from exc

            if _should_retry_status(response.status_code) and attempt < self._options.max_retries:
                await asyncio.sleep(_retry_sleep(attempt))
                attempt += 1
                continue

            return _parse_response(response)


# ---------------------------------------------------------------------------
# Helper used by sync and async resources
# ---------------------------------------------------------------------------


def extract_results(envelope: Any) -> Any:
    """Return the ``results`` field of an envelope payload, else the payload itself."""
    if isinstance(envelope, dict) and "results" in envelope:
        return envelope["results"]
    return envelope


# Typed alias for resource-method retry-friendly callables (unused here but exported).
SyncCall = Callable[..., Response]
AsyncCall = Callable[..., Awaitable[Response]]

__all__ = [
    "ClientOptions",
    "Response",
    "Transport",
    "AsyncTransport",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "serialize_params",
    "build_url",
    "resolve_api_key",
    "build_auth_headers",
    "require_api_key",
    "extract_results",
]
