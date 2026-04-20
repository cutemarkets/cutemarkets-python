"""Synchronous :class:`CuteMarkets` client."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from ._transport import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    ClientOptions,
    Transport,
    resolve_api_key,
)
from .models.common import RateLimitInfo, SystemStatus
from .resources.options import OptionsResource
from .resources.status import StatusResource
from .resources.tickers import TickersResource


class CuteMarkets:
    """Synchronous client for the CuteMarkets v1 REST API.

    API keys are prefixed ``cm_...``. The client resolves credentials in
    this order:

    1. Explicit ``api_key`` argument.
    2. ``CUTEMARKETS_API_KEY`` environment variable.
    3. Unset — only :meth:`status` works in this mode.

    Example:

    .. code-block:: python

        from cutemarkets import CuteMarkets

        client = CuteMarkets(api_key="cm_...")
        chain = client.options.chain("NFLX", limit=5)
        for contract in chain:
            print(contract.details.ticker, contract.break_even_price)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        headers: Optional[Dict[str, str]] = None,
        transport: Optional[httpx.BaseTransport] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        options = ClientOptions(
            api_key=resolve_api_key(api_key),
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=dict(headers) if headers else {},
        )
        self._transport = Transport(
            options,
            httpx_transport=transport,
            client=http_client,
        )
        self._status = StatusResource(self._transport)
        self.tickers = TickersResource(self._transport)
        self.options = OptionsResource(self._transport)

    # ---------------- public config ----------------

    @property
    def api_key(self) -> Optional[str]:
        return self._transport.api_key

    def set_api_key(self, api_key: Optional[str]) -> None:
        """Swap in a new API key (or clear it with ``None``)."""
        self._transport.set_api_key(api_key)

    @property
    def base_url(self) -> str:
        return self._transport.options.base_url

    # ---------------- status ----------------

    def status(self) -> SystemStatus:
        """Poll the unauthenticated ``/v1/status/`` health endpoint."""
        return self._status()

    # ---------------- lifecycle ----------------

    def close(self) -> None:
        """Release the underlying HTTP client's resources."""
        self._transport.close()

    def __enter__(self) -> "CuteMarkets":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


__all__ = ["CuteMarkets"]
