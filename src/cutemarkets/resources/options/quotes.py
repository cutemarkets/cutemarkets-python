"""``/v1/options/quotes/`` — historical NBBO quotes (Expert Plan only)."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator

from ..._pagination import AsyncPage, Page
from ..._transport import AsyncTransport, Transport
from ...models.options import Quote
from .._base import quote_path


def _path(options_ticker: str) -> str:
    return f"/v1/options/quotes/{quote_path(options_ticker)}/"


class QuotesResource:
    """Sync quotes resource.

    See [docs/quotes.md](https://cutemarkets.com/docs/quotes). Expert Plan
    required — non-Expert keys receive HTTP 403 (mapped to
    :class:`cutemarkets.errors.ForbiddenError`).
    """

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def list(self, options_ticker: str, **filters: Any) -> Page[Quote]:
        response = self._t.request("GET", _path(options_ticker), params=filters)
        return Page.from_response(response, transport=self._t, parser=Quote.model_validate)

    def iter_list(self, options_ticker: str, **filters: Any) -> Iterator[Quote]:
        page = self.list(options_ticker, **filters)
        yield from page.iter_all()


class AsyncQuotesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def list(self, options_ticker: str, **filters: Any) -> AsyncPage[Quote]:
        response = await self._t.request("GET", _path(options_ticker), params=filters)
        return AsyncPage.from_response(
            response, transport=self._t, parser=Quote.model_validate
        )

    async def iter_list(
        self,
        options_ticker: str,
        **filters: Any,
    ) -> AsyncIterator[Quote]:
        page = await self.list(options_ticker, **filters)
        async for item in page.iter_all():
            yield item


__all__ = ["QuotesResource", "AsyncQuotesResource"]
