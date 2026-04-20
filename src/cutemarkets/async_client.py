"""Asynchronous :class:`AsyncCuteMarkets` client."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from ._transport import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncTransport,
    ClientOptions,
    resolve_api_key,
)
from .models.common import SystemStatus
from .resources.options import AsyncOptionsResource
from .resources.status import AsyncStatusResource
from .resources.tickers import AsyncTickersResource


class AsyncCuteMarkets:
    """Asynchronous client for the CuteMarkets v1 REST API.

    Mirrors :class:`cutemarkets.CuteMarkets` — every method that performs
    I/O is an ``async def`` and returns the same response types. Pagination
    generators are async iterators (use ``async for``).

    Example:

    .. code-block:: python

        import asyncio
        from cutemarkets import AsyncCuteMarkets

        async def main():
            async with AsyncCuteMarkets(api_key="cm_...") as client:
                chain = await client.options.chain("NFLX", limit=5)
                async for contract in client.options.iter_chain("NFLX", limit=5):
                    print(contract.details.ticker)

        asyncio.run(main())
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        headers: Optional[Dict[str, str]] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        options = ClientOptions(
            api_key=resolve_api_key(api_key),
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=dict(headers) if headers else {},
        )
        self._transport = AsyncTransport(
            options,
            httpx_transport=transport,
            client=http_client,
        )
        self._status = AsyncStatusResource(self._transport)
        self.tickers = AsyncTickersResource(self._transport)
        self.options = AsyncOptionsResource(self._transport)

    @property
    def api_key(self) -> Optional[str]:
        return self._transport.api_key

    def set_api_key(self, api_key: Optional[str]) -> None:
        self._transport.set_api_key(api_key)

    @property
    def base_url(self) -> str:
        return self._transport.options.base_url

    async def status(self) -> SystemStatus:
        """Poll the unauthenticated ``/v1/status/`` health endpoint."""
        return await self._status()

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> "AsyncCuteMarkets":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()


__all__ = ["AsyncCuteMarkets"]
