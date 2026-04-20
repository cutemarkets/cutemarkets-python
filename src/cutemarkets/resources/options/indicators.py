"""``/v1/options/indicators/`` — SMA / EMA / MACD / RSI."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator, Optional

from ..._transport import AsyncTransport, Response, Transport
from ...models.indicators import (
    IndicatorResult,
    IndicatorValue,
    MacdResult,
    MacdValue,
)
from .._base import quote_path


def _path(kind: str, ticker: str) -> str:
    return f"/v1/options/indicators/{kind}/{quote_path(ticker)}/"


def _parse_indicator(response: Response) -> IndicatorResult:
    data = response.data if isinstance(response.data, dict) else {}
    results = data.get("results", {})
    return IndicatorResult.model_validate(results)


def _parse_macd(response: Response) -> MacdResult:
    data = response.data if isinstance(response.data, dict) else {}
    results = data.get("results", {})
    return MacdResult.model_validate(results)


class IndicatorsResource:
    """Sync indicators resource.

    See [docs/indicators-sma.md](https://cutemarkets.com/docs/indicators-sma),
    [docs/indicators-ema.md](https://cutemarkets.com/docs/indicators-ema),
    [docs/indicators-macd.md](https://cutemarkets.com/docs/indicators-macd), and
    [docs/indicators-rsi.md](https://cutemarkets.com/docs/indicators-rsi).
    """

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def _fetch(self, kind: str, ticker: str, filters: dict[str, Any]) -> IndicatorResult:
        response = self._t.request("GET", _path(kind, ticker), params=filters)
        return _parse_indicator(response)

    def sma(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> IndicatorResult:
        """Simple Moving Average."""
        return self._fetch(
            "sma",
            ticker,
            {
                "timespan": timespan,
                "window": window,
                "series_type": series_type,
                "adjusted": adjusted,
                "expand_underlying": expand_underlying,
                "order": order,
                "limit": limit,
                **filters,
            },
        )

    def ema(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> IndicatorResult:
        """Exponential Moving Average."""
        return self._fetch(
            "ema",
            ticker,
            {
                "timespan": timespan,
                "window": window,
                "series_type": series_type,
                "adjusted": adjusted,
                "expand_underlying": expand_underlying,
                "order": order,
                "limit": limit,
                **filters,
            },
        )

    def macd(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        short_window: Optional[int] = None,
        long_window: Optional[int] = None,
        signal_window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> MacdResult:
        """Moving Average Convergence / Divergence."""
        params = {
            "timespan": timespan,
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
            "series_type": series_type,
            "adjusted": adjusted,
            "expand_underlying": expand_underlying,
            "order": order,
            "limit": limit,
            **filters,
        }
        response = self._t.request("GET", _path("macd", ticker), params=params)
        return _parse_macd(response)

    def rsi(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> IndicatorResult:
        """Relative Strength Index."""
        return self._fetch(
            "rsi",
            ticker,
            {
                "timespan": timespan,
                "window": window,
                "series_type": series_type,
                "adjusted": adjusted,
                "expand_underlying": expand_underlying,
                "order": order,
                "limit": limit,
                **filters,
            },
        )


class AsyncIndicatorsResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def _fetch(
        self, kind: str, ticker: str, filters: dict[str, Any]
    ) -> IndicatorResult:
        response = await self._t.request("GET", _path(kind, ticker), params=filters)
        return _parse_indicator(response)

    async def sma(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> IndicatorResult:
        return await self._fetch(
            "sma",
            ticker,
            {
                "timespan": timespan,
                "window": window,
                "series_type": series_type,
                "adjusted": adjusted,
                "expand_underlying": expand_underlying,
                "order": order,
                "limit": limit,
                **filters,
            },
        )

    async def ema(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> IndicatorResult:
        return await self._fetch(
            "ema",
            ticker,
            {
                "timespan": timespan,
                "window": window,
                "series_type": series_type,
                "adjusted": adjusted,
                "expand_underlying": expand_underlying,
                "order": order,
                "limit": limit,
                **filters,
            },
        )

    async def macd(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        short_window: Optional[int] = None,
        long_window: Optional[int] = None,
        signal_window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> MacdResult:
        params = {
            "timespan": timespan,
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
            "series_type": series_type,
            "adjusted": adjusted,
            "expand_underlying": expand_underlying,
            "order": order,
            "limit": limit,
            **filters,
        }
        response = await self._t.request("GET", _path("macd", ticker), params=params)
        return _parse_macd(response)

    async def rsi(
        self,
        ticker: str,
        *,
        timespan: Optional[str] = None,
        window: Optional[int] = None,
        series_type: Optional[str] = None,
        adjusted: Optional[bool] = None,
        expand_underlying: Optional[bool] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> IndicatorResult:
        return await self._fetch(
            "rsi",
            ticker,
            {
                "timespan": timespan,
                "window": window,
                "series_type": series_type,
                "adjusted": adjusted,
                "expand_underlying": expand_underlying,
                "order": order,
                "limit": limit,
                **filters,
            },
        )


__all__ = [
    "IndicatorsResource",
    "AsyncIndicatorsResource",
    "IndicatorValue",
    "MacdValue",
]
