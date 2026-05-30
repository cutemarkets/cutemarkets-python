"""``client.stocks`` namespace for stock market data and reference data."""

from __future__ import annotations

import datetime as _dt
from typing import Any, AsyncIterator, Iterator, Optional, Union

from .._pagination import AsyncPage, Page
from .._transport import DEFAULT_AUTH_KEY, AsyncTransport, Transport
from ..models.indicators import IndicatorResult, MacdResult
from ..models.stocks import (
    StockAggregate,
    StockGroupedDaily,
    StockLastQuote,
    StockLastTrade,
    StockOpenClose,
    StockQuote,
    StockRelatedTicker,
    StockSnapshot,
    StockSnapshotResponse,
    StockTicker,
    StockTickerType,
    StockTrade,
)
from ._base import _parse_single, quote_path

DateLike = Union[str, int, _dt.date, _dt.datetime]


def _coerce_date(value: DateLike) -> str:
    if isinstance(value, _dt.datetime):
        return value.date().isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    return str(value)


def _snapshot_from_response(data: Any) -> StockSnapshot:
    if isinstance(data, dict):
        if isinstance(data.get("results"), dict):
            return StockSnapshot.model_validate(data["results"])
        if isinstance(data.get("ticker"), dict):
            return StockSnapshot.model_validate(data["ticker"])
    return StockSnapshot.model_validate(data)


def _parse_indicator_payload(data: Any) -> IndicatorResult:
    payload = data if isinstance(data, dict) else {}
    return IndicatorResult.model_validate(payload.get("results", payload))


def _parse_macd_payload(data: Any) -> MacdResult:
    payload = data if isinstance(data, dict) else {}
    return MacdResult.model_validate(payload.get("results", payload))


class StockSnapshotsResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def all(self, **params: Any) -> StockSnapshotResponse:
        response = self._t.request("GET", "/v1/stocks/snapshot/", params=params, api_key=self._api_key)
        return StockSnapshotResponse.model_validate(response.data)

    def get(self, ticker: str, **params: Any) -> StockSnapshot:
        response = self._t.request(
            "GET",
            f"/v1/stocks/snapshot/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _snapshot_from_response(response.data)

    def movers(self, direction: str, **params: Any) -> StockSnapshotResponse:
        response = self._t.request(
            "GET",
            f"/v1/stocks/snapshot/movers/{quote_path(direction)}/",
            params=params,
            api_key=self._api_key,
        )
        return StockSnapshotResponse.model_validate(response.data)


class AsyncStockSnapshotsResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def all(self, **params: Any) -> StockSnapshotResponse:
        response = await self._t.request("GET", "/v1/stocks/snapshot/", params=params, api_key=self._api_key)
        return StockSnapshotResponse.model_validate(response.data)

    async def get(self, ticker: str, **params: Any) -> StockSnapshot:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/snapshot/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _snapshot_from_response(response.data)

    async def movers(self, direction: str, **params: Any) -> StockSnapshotResponse:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/snapshot/movers/{quote_path(direction)}/",
            params=params,
            api_key=self._api_key,
        )
        return StockSnapshotResponse.model_validate(response.data)


class StockTickersResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def list(self, **params: Any) -> Page[StockTicker]:
        response = self._t.request("GET", "/v1/stocks/tickers/", params=params, api_key=self._api_key)
        return Page.from_response(
            response,
            transport=self._t,
            parser=StockTicker.model_validate,
            api_key=self._api_key,
        )

    def iter_list(self, **params: Any) -> Iterator[StockTicker]:
        page = self.list(**params)
        yield from page.iter_all()

    def types(self, **params: Any) -> Page[StockTickerType]:
        response = self._t.request("GET", "/v1/stocks/tickers/types/", params=params, api_key=self._api_key)
        return Page.from_response(
            response,
            transport=self._t,
            parser=StockTickerType.model_validate,
            api_key=self._api_key,
        )

    def get(self, ticker: str, **params: Any) -> StockTicker:
        response = self._t.request(
            "GET",
            f"/v1/stocks/tickers/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockTicker.model_validate)

    def related(self, ticker: str, **params: Any) -> Page[StockRelatedTicker]:
        response = self._t.request(
            "GET",
            f"/v1/stocks/tickers/{quote_path(ticker)}/related/",
            params=params,
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=StockRelatedTicker.model_validate,
            api_key=self._api_key,
        )


class AsyncStockTickersResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def list(self, **params: Any) -> AsyncPage[StockTicker]:
        response = await self._t.request("GET", "/v1/stocks/tickers/", params=params, api_key=self._api_key)
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=StockTicker.model_validate,
            api_key=self._api_key,
        )

    async def iter_list(self, **params: Any) -> AsyncIterator[StockTicker]:
        page = await self.list(**params)
        async for item in page.iter_all():
            yield item

    async def types(self, **params: Any) -> AsyncPage[StockTickerType]:
        response = await self._t.request("GET", "/v1/stocks/tickers/types/", params=params, api_key=self._api_key)
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=StockTickerType.model_validate,
            api_key=self._api_key,
        )

    async def get(self, ticker: str, **params: Any) -> StockTicker:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/tickers/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockTicker.model_validate)

    async def related(self, ticker: str, **params: Any) -> AsyncPage[StockRelatedTicker]:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/tickers/{quote_path(ticker)}/related/",
            params=params,
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=StockRelatedTicker.model_validate,
            api_key=self._api_key,
        )


class StockTradesResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def list(self, ticker: str, **params: Any) -> Page[StockTrade]:
        response = self._t.request(
            "GET",
            f"/v1/stocks/trades/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=StockTrade.model_validate,
            api_key=self._api_key,
        )

    def iter_list(self, ticker: str, **params: Any) -> Iterator[StockTrade]:
        page = self.list(ticker, **params)
        yield from page.iter_all()

    def last(self, ticker: str, **params: Any) -> StockLastTrade:
        response = self._t.request(
            "GET",
            f"/v1/stocks/trades/{quote_path(ticker)}/last/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockLastTrade.model_validate)


class AsyncStockTradesResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def list(self, ticker: str, **params: Any) -> AsyncPage[StockTrade]:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/trades/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=StockTrade.model_validate,
            api_key=self._api_key,
        )

    async def iter_list(self, ticker: str, **params: Any) -> AsyncIterator[StockTrade]:
        page = await self.list(ticker, **params)
        async for item in page.iter_all():
            yield item

    async def last(self, ticker: str, **params: Any) -> StockLastTrade:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/trades/{quote_path(ticker)}/last/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockLastTrade.model_validate)


class StockQuotesResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def list(self, ticker: str, **params: Any) -> Page[StockQuote]:
        response = self._t.request(
            "GET",
            f"/v1/stocks/quotes/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=StockQuote.model_validate,
            api_key=self._api_key,
        )

    def iter_list(self, ticker: str, **params: Any) -> Iterator[StockQuote]:
        page = self.list(ticker, **params)
        yield from page.iter_all()

    def last(self, ticker: str, **params: Any) -> StockLastQuote:
        response = self._t.request(
            "GET",
            f"/v1/stocks/quotes/{quote_path(ticker)}/last/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockLastQuote.model_validate)


class AsyncStockQuotesResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def list(self, ticker: str, **params: Any) -> AsyncPage[StockQuote]:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/quotes/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=StockQuote.model_validate,
            api_key=self._api_key,
        )

    async def iter_list(self, ticker: str, **params: Any) -> AsyncIterator[StockQuote]:
        page = await self.list(ticker, **params)
        async for item in page.iter_all():
            yield item

    async def last(self, ticker: str, **params: Any) -> StockLastQuote:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/quotes/{quote_path(ticker)}/last/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockLastQuote.model_validate)


class StockAggsResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def grouped(self, date: DateLike, **params: Any) -> Page[StockGroupedDaily]:
        response = self._t.request(
            "GET",
            f"/v1/stocks/aggs/grouped/{_coerce_date(date)}/",
            params=params,
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=StockGroupedDaily.model_validate,
            api_key=self._api_key,
        )

    def range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        **params: Any,
    ) -> Page[StockAggregate]:
        response = self._t.request(
            "GET",
            (
                f"/v1/stocks/aggs/{quote_path(ticker)}/{multiplier}/{quote_path(timespan)}/"
                f"{_coerce_date(from_date)}/{_coerce_date(to_date)}/"
            ),
            params=params,
            api_key=self._api_key,
        )
        return Page.from_response(
            response,
            transport=self._t,
            parser=StockAggregate.model_validate,
            api_key=self._api_key,
        )

    def iter_range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        **params: Any,
    ) -> Iterator[StockAggregate]:
        page = self.range(ticker, multiplier, timespan, from_date, to_date, **params)
        yield from page.iter_all()

    def previous(self, ticker: str, **params: Any) -> StockAggregate:
        response = self._t.request(
            "GET",
            f"/v1/stocks/aggs/{quote_path(ticker)}/prev/",
            params=params,
            api_key=self._api_key,
        )
        data = response.data
        results = data.get("results") if isinstance(data, dict) else None
        if isinstance(results, list) and results:
            return StockAggregate.model_validate(results[0])
        return _parse_single(data, StockAggregate.model_validate)

    def open_close(self, ticker: str, date: DateLike, **params: Any) -> StockOpenClose:
        response = self._t.request(
            "GET",
            f"/v1/stocks/open-close/{quote_path(ticker)}/{_coerce_date(date)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockOpenClose.model_validate)


class AsyncStockAggsResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def grouped(self, date: DateLike, **params: Any) -> AsyncPage[StockGroupedDaily]:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/aggs/grouped/{_coerce_date(date)}/",
            params=params,
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=StockGroupedDaily.model_validate,
            api_key=self._api_key,
        )

    async def range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        **params: Any,
    ) -> AsyncPage[StockAggregate]:
        response = await self._t.request(
            "GET",
            (
                f"/v1/stocks/aggs/{quote_path(ticker)}/{multiplier}/{quote_path(timespan)}/"
                f"{_coerce_date(from_date)}/{_coerce_date(to_date)}/"
            ),
            params=params,
            api_key=self._api_key,
        )
        return AsyncPage.from_response(
            response,
            transport=self._t,
            parser=StockAggregate.model_validate,
            api_key=self._api_key,
        )

    async def iter_range(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_date: DateLike,
        to_date: DateLike,
        **params: Any,
    ) -> AsyncIterator[StockAggregate]:
        page = await self.range(ticker, multiplier, timespan, from_date, to_date, **params)
        async for item in page.iter_all():
            yield item

    async def previous(self, ticker: str, **params: Any) -> StockAggregate:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/aggs/{quote_path(ticker)}/prev/",
            params=params,
            api_key=self._api_key,
        )
        data = response.data
        results = data.get("results") if isinstance(data, dict) else None
        if isinstance(results, list) and results:
            return StockAggregate.model_validate(results[0])
        return _parse_single(data, StockAggregate.model_validate)

    async def open_close(self, ticker: str, date: DateLike, **params: Any) -> StockOpenClose:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/open-close/{quote_path(ticker)}/{_coerce_date(date)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_single(response.data, StockOpenClose.model_validate)


class StockIndicatorsResource:
    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    def _fetch(self, kind: str, ticker: str, params: dict[str, Any]) -> IndicatorResult:
        response = self._t.request(
            "GET",
            f"/v1/stocks/indicators/{kind}/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_indicator_payload(response.data)

    def sma(self, ticker: str, **params: Any) -> IndicatorResult:
        return self._fetch("sma", ticker, params)

    def ema(self, ticker: str, **params: Any) -> IndicatorResult:
        return self._fetch("ema", ticker, params)

    def rsi(self, ticker: str, **params: Any) -> IndicatorResult:
        return self._fetch("rsi", ticker, params)

    def macd(self, ticker: str, **params: Any) -> MacdResult:
        response = self._t.request(
            "GET",
            f"/v1/stocks/indicators/macd/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_macd_payload(response.data)


class AsyncStockIndicatorsResource:
    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self._api_key = api_key

    async def _fetch(self, kind: str, ticker: str, params: dict[str, Any]) -> IndicatorResult:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/indicators/{kind}/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_indicator_payload(response.data)

    async def sma(self, ticker: str, **params: Any) -> IndicatorResult:
        return await self._fetch("sma", ticker, params)

    async def ema(self, ticker: str, **params: Any) -> IndicatorResult:
        return await self._fetch("ema", ticker, params)

    async def rsi(self, ticker: str, **params: Any) -> IndicatorResult:
        return await self._fetch("rsi", ticker, params)

    async def macd(self, ticker: str, **params: Any) -> MacdResult:
        response = await self._t.request(
            "GET",
            f"/v1/stocks/indicators/macd/{quote_path(ticker)}/",
            params=params,
            api_key=self._api_key,
        )
        return _parse_macd_payload(response.data)


class StocksResource:
    """Sync ``client.stocks`` namespace."""

    def __init__(self, transport: Transport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self.snapshots = StockSnapshotsResource(transport, api_key=api_key)
        self.tickers = StockTickersResource(transport, api_key=api_key)
        self.trades = StockTradesResource(transport, api_key=api_key)
        self.quotes = StockQuotesResource(transport, api_key=api_key)
        self.aggs = StockAggsResource(transport, api_key=api_key)
        self.indicators = StockIndicatorsResource(transport, api_key=api_key)

    def snapshot(self, ticker: str, **params: Any) -> StockSnapshot:
        return self.snapshots.get(ticker, **params)

    def open_close(self, ticker: str, date: DateLike, **params: Any) -> StockOpenClose:
        return self.aggs.open_close(ticker, date, **params)


class AsyncStocksResource:
    """Async ``client.stocks`` namespace."""

    def __init__(self, transport: AsyncTransport, *, api_key: Any = DEFAULT_AUTH_KEY) -> None:
        self._t = transport
        self.snapshots = AsyncStockSnapshotsResource(transport, api_key=api_key)
        self.tickers = AsyncStockTickersResource(transport, api_key=api_key)
        self.trades = AsyncStockTradesResource(transport, api_key=api_key)
        self.quotes = AsyncStockQuotesResource(transport, api_key=api_key)
        self.aggs = AsyncStockAggsResource(transport, api_key=api_key)
        self.indicators = AsyncStockIndicatorsResource(transport, api_key=api_key)

    async def snapshot(self, ticker: str, **params: Any) -> StockSnapshot:
        return await self.snapshots.get(ticker, **params)

    async def open_close(self, ticker: str, date: DateLike, **params: Any) -> StockOpenClose:
        return await self.aggs.open_close(ticker, date, **params)


__all__ = ["StocksResource", "AsyncStocksResource", "DateLike"]
