"""``/v1/options/trades/`` — historical trades + last trade."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator

from ..._pagination import AsyncPage, Page
from ..._transport import AsyncTransport, Transport
from ...models.options import LastTrade, Trade
from .._base import _parse_single, quote_path


def _list_path(options_ticker: str) -> str:
    return f"/v1/options/trades/{quote_path(options_ticker)}/"


def _last_path(options_ticker: str) -> str:
    return f"/v1/options/trades/{quote_path(options_ticker)}/last/"


class TradesResource:
    """Sync trades resource.

    See [docs/trades.md](https://cutemarkets.com/docs/trades).
    """

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def list(self, options_ticker: str, **filters: Any) -> Page[Trade]:
        """Historical trades for one contract.

        Supports ``timestamp`` / ``timestamp_gte`` / ``timestamp_gt`` /
        ``timestamp_lte`` / ``timestamp_lt`` filters, plus ``sort``, ``order``,
        ``limit``, and ``page``.
        """
        response = self._t.request("GET", _list_path(options_ticker), params=filters)
        return Page.from_response(response, transport=self._t, parser=Trade.model_validate)

    def iter_list(self, options_ticker: str, **filters: Any) -> Iterator[Trade]:
        """Auto-paginate historical trades."""
        page = self.list(options_ticker, **filters)
        yield from page.iter_all()

    def last(self, options_ticker: str) -> LastTrade:
        """Return the latest trade for one contract (compact shape).

        The response uses abbreviated keys (``T``, ``p``, ``s``, ...). The
        returned :class:`LastTrade` exposes readable property aliases
        (``ticker``, ``price``, ``size``, ...) for convenience.
        """
        response = self._t.request("GET", _last_path(options_ticker))
        return _parse_single(response.data, LastTrade.model_validate)


class AsyncTradesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def list(self, options_ticker: str, **filters: Any) -> AsyncPage[Trade]:
        response = await self._t.request("GET", _list_path(options_ticker), params=filters)
        return AsyncPage.from_response(
            response, transport=self._t, parser=Trade.model_validate
        )

    async def iter_list(
        self,
        options_ticker: str,
        **filters: Any,
    ) -> AsyncIterator[Trade]:
        page = await self.list(options_ticker, **filters)
        async for item in page.iter_all():
            yield item

    async def last(self, options_ticker: str) -> LastTrade:
        response = await self._t.request("GET", _last_path(options_ticker))
        return _parse_single(response.data, LastTrade.model_validate)


__all__ = ["TradesResource", "AsyncTradesResource"]
