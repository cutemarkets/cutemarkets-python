"""``/v1/options/aggs/`` — OHLC aggregates (custom range + previous day).

``aggs.open_close(...)`` is grouped here for discoverability, though the
underlying route is ``/v1/options/open-close/`` (not under ``/aggs/``).
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, AsyncIterator, Iterator, Optional, Union

from ..._pagination import AsyncPage, Page
from ..._transport import AsyncTransport, Transport
from ...models.options import Aggregate, OpenClose
from .._base import _parse_single, quote_path
from .open_close import AsyncOpenCloseResource, OpenCloseResource

DateLike = Union[str, int, _dt.date, _dt.datetime]


def _coerce_range_bound(value: DateLike) -> str:
    """Serialize a from/to bound.

    The API accepts ``YYYY-MM-DD`` or a millisecond Unix timestamp as a
    string. We keep the caller's intent: dates become ISO strings, ints stay
    as their decimal form.
    """
    if isinstance(value, _dt.datetime):
        return value.date().isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    return str(value)


def _range_path(ticker: str, multiplier: int, timespan: str, frm: DateLike, to: DateLike) -> str:
    return (
        f"/v1/options/aggs/{quote_path(ticker)}/{multiplier}/{timespan}/"
        f"{_coerce_range_bound(frm)}/{_coerce_range_bound(to)}/"
    )


def _previous_path(ticker: str) -> str:
    return f"/v1/options/aggs/{quote_path(ticker)}/prev/"


class AggsResource:
    """Sync aggregates resource.

    See [docs/aggregates.md](https://cutemarkets.com/docs/aggregates).
    """

    def __init__(self, transport: Transport) -> None:
        self._t = transport
        self._open_close = OpenCloseResource(transport)

    def range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        *,
        adjusted: Optional[bool] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        **extra: Any,
    ) -> Page[Aggregate]:
        """Custom-range OHLC bars."""
        params = {
            "adjusted": adjusted,
            "sort": sort,
            "limit": limit,
            **extra,
        }
        response = self._t.request(
            "GET",
            _range_path(ticker, multiplier, timespan, from_date, to_date),
            params=params,
        )
        return Page.from_response(response, transport=self._t, parser=Aggregate.model_validate)

    def iter_range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        **kwargs: Any,
    ) -> Iterator[Aggregate]:
        """Auto-paginate :meth:`range`, yielding one bar at a time."""
        page = self.range(ticker, multiplier, timespan, from_date, to_date, **kwargs)
        yield from page.iter_all()

    def previous(
        self,
        ticker: str,
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> Aggregate:
        """Previous trading day's daily bar."""
        params = {"adjusted": adjusted, **extra}
        response = self._t.request("GET", _previous_path(ticker), params=params)
        data = response.data
        results = data.get("results") if isinstance(data, dict) else None
        if isinstance(results, list) and results:
            return Aggregate.model_validate(results[0])
        if isinstance(results, dict):
            return Aggregate.model_validate(results)
        return _parse_single(data, Aggregate.model_validate)

    def open_close(
        self,
        ticker: str,
        date: Union[str, _dt.date, _dt.datetime],
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> OpenClose:
        """Regular-session open/close for a single calendar date."""
        return self._open_close(ticker, date, adjusted=adjusted, **extra)


class AsyncAggsResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport
        self._open_close = AsyncOpenCloseResource(transport)

    async def range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        *,
        adjusted: Optional[bool] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        **extra: Any,
    ) -> AsyncPage[Aggregate]:
        params = {
            "adjusted": adjusted,
            "sort": sort,
            "limit": limit,
            **extra,
        }
        response = await self._t.request(
            "GET",
            _range_path(ticker, multiplier, timespan, from_date, to_date),
            params=params,
        )
        return AsyncPage.from_response(
            response, transport=self._t, parser=Aggregate.model_validate
        )

    async def iter_range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        **kwargs: Any,
    ) -> AsyncIterator[Aggregate]:
        page = await self.range(ticker, multiplier, timespan, from_date, to_date, **kwargs)
        async for item in page.iter_all():
            yield item

    async def previous(
        self,
        ticker: str,
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> Aggregate:
        params = {"adjusted": adjusted, **extra}
        response = await self._t.request("GET", _previous_path(ticker), params=params)
        data = response.data
        results = data.get("results") if isinstance(data, dict) else None
        if isinstance(results, list) and results:
            return Aggregate.model_validate(results[0])
        if isinstance(results, dict):
            return Aggregate.model_validate(results)
        return _parse_single(data, Aggregate.model_validate)

    async def open_close(
        self,
        ticker: str,
        date: Union[str, _dt.date, _dt.datetime],
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> OpenClose:
        return await self._open_close(ticker, date, adjusted=adjusted, **extra)


__all__ = ["AggsResource", "AsyncAggsResource", "DateLike"]
