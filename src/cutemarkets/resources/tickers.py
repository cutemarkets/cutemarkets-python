"""``/v1/tickers/`` resource — search + expirations."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator, Optional

from .._pagination import AsyncPage, Page
from .._transport import AsyncTransport, Transport
from ..models.tickers import ExpirationsResponse, TickerSearchResult
from ._base import quote_path


class TickersResource:
    """Sync ``/v1/tickers/`` resource."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def search(
        self,
        *,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> Page[TickerSearchResult]:
        """Search for underlying ticker symbols.

        See [docs/ticker-search.md](https://cutemarkets.com/docs/ticker-search).
        """
        params = {"query": query, "limit": limit, **filters}
        response = self._t.request("GET", "/v1/tickers/search/", params=params)
        return Page.from_response(
            response, transport=self._t, parser=TickerSearchResult.model_validate
        )

    def iter_search(
        self,
        *,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> Iterator[TickerSearchResult]:
        """Auto-paginate :meth:`search`, yielding one row at a time."""
        page = self.search(query=query, limit=limit, **filters)
        yield from page.iter_all()

    def expirations(self, ticker: str) -> ExpirationsResponse:
        """Return every expiration date available for an underlying.

        See [docs/expirations.md](https://cutemarkets.com/docs/expirations).
        """
        path = f"/v1/tickers/expirations/{quote_path(ticker)}/"
        response = self._t.request("GET", path)
        return ExpirationsResponse.model_validate(response.data)


class AsyncTickersResource:
    """Async ``/v1/tickers/`` resource."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def search(
        self,
        *,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> AsyncPage[TickerSearchResult]:
        params = {"query": query, "limit": limit, **filters}
        response = await self._t.request("GET", "/v1/tickers/search/", params=params)
        return AsyncPage.from_response(
            response, transport=self._t, parser=TickerSearchResult.model_validate
        )

    async def iter_search(
        self,
        *,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> AsyncIterator[TickerSearchResult]:
        page = await self.search(query=query, limit=limit, **filters)
        async for item in page.iter_all():
            yield item

    async def expirations(self, ticker: str) -> ExpirationsResponse:
        path = f"/v1/tickers/expirations/{quote_path(ticker)}/"
        response = await self._t.request("GET", path)
        return ExpirationsResponse.model_validate(response.data)


__all__ = ["TickersResource", "AsyncTickersResource"]
