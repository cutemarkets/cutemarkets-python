"""Response models for technical-indicator endpoints (SMA / EMA / MACD / RSI)."""

from __future__ import annotations

from typing import Any, List, Optional

from ._base import CuteBase


class IndicatorValue(CuteBase):
    """One point in an SMA / EMA / RSI series."""

    timestamp: Optional[int] = None
    value: Optional[float] = None


class MacdValue(IndicatorValue):
    """One point in an MACD series.

    MACD adds the ``signal`` and ``histogram`` lines on top of the shared
    ``timestamp`` / ``value`` pair used by single-line indicators.
    """

    signal: Optional[float] = None
    histogram: Optional[float] = None


class IndicatorUnderlying(CuteBase):
    """Optional ``results.underlying`` block when ``expand_underlying=True``."""

    url: Optional[str] = None
    aggregates: Optional[List[Any]] = None


class IndicatorResult(CuteBase):
    """``results`` block for indicator endpoints."""

    values: List[IndicatorValue] = []
    underlying: Optional[IndicatorUnderlying] = None


class MacdResult(CuteBase):
    """``results`` block for the MACD endpoint."""

    values: List[MacdValue] = []
    underlying: Optional[IndicatorUnderlying] = None


__all__ = [
    "IndicatorValue",
    "MacdValue",
    "IndicatorUnderlying",
    "IndicatorResult",
    "MacdResult",
]
