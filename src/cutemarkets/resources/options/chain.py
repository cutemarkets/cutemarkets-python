"""``/v1/options/chain/{ticker}/`` — option chain snapshot."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator

from ..._pagination import AsyncPage, Page
from ..._transport import AsyncTransport, Transport
from ...models.options import ContractSnapshot
from .._base import quote_path


def _path(ticker: str) -> str:
    return f"/v1/options/chain/{quote_path(ticker)}/"


class ChainResource:
    """Sync option-chain resource.

    See [docs/option-chain.md](https://cutemarkets.com/docs/option-chain).
    """

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def __call__(self, ticker: str, **filters: Any) -> Page[ContractSnapshot]:
        """Fetch one page of the option chain for an underlying.

        Supports range filters via ``_gte`` / ``_gt`` / ``_lte`` / ``_lt``
        suffixes (e.g. ``strike_price_gte=90``).
        """
        response = self._t.request("GET", _path(ticker), params=filters)
        return Page.from_response(
            response, transport=self._t, parser=ContractSnapshot.model_validate
        )

    def iter(self, ticker: str, **filters: Any) -> Iterator[ContractSnapshot]:
        """Auto-paginate the option chain, yielding one contract at a time."""
        page = self(ticker, **filters)
        yield from page.iter_all()


class AsyncChainResource:
    """Async option-chain resource."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def __call__(self, ticker: str, **filters: Any) -> AsyncPage[ContractSnapshot]:
        response = await self._t.request("GET", _path(ticker), params=filters)
        return AsyncPage.from_response(
            response, transport=self._t, parser=ContractSnapshot.model_validate
        )

    async def iter(
        self,
        ticker: str,
        **filters: Any,
    ) -> AsyncIterator[ContractSnapshot]:
        page = await self(ticker, **filters)
        async for item in page.iter_all():
            yield item


__all__ = ["ChainResource", "AsyncChainResource"]
