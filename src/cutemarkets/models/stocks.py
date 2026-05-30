"""Response models for ``/v1/stocks/...`` endpoints."""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import Field

from ._base import CuteBase
from .options import Aggregate, LastTrade, OpenClose


class StockSnapshot(CuteBase):
    """Flexible stock snapshot row.

    Snapshot payloads differ by endpoint and upstream source. Known fields are
    exposed directly while unknown fields remain available via ``raw``.
    """

    ticker: Optional[Any] = None
    day: Optional[Any] = None
    min: Optional[Any] = None
    prevDay: Optional[Any] = None
    lastTrade: Optional[Any] = None
    lastQuote: Optional[Any] = None
    updated: Optional[int] = None


class StockSnapshotResponse(CuteBase):
    status: Optional[str] = None
    request_id: Optional[str] = None
    tickers: List[StockSnapshot] = []
    results: List[StockSnapshot] = []
    ticker: Optional[StockSnapshot] = None


class StockTicker(CuteBase):
    ticker: Optional[str] = None
    name: Optional[str] = None
    market: Optional[str] = None
    locale: Optional[str] = None
    primary_exchange: Optional[str] = None
    type: Optional[str] = None
    active: Optional[bool] = None
    currency_name: Optional[str] = None
    cik: Optional[str] = None
    composite_figi: Optional[str] = None
    share_class_figi: Optional[str] = None
    last_updated_utc: Optional[str] = None


class StockTickerType(CuteBase):
    code: Optional[str] = None
    description: Optional[str] = None
    asset_class: Optional[str] = None
    locale: Optional[str] = None


class StockRelatedTicker(CuteBase):
    ticker: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None


class StockTrade(CuteBase):
    conditions: Optional[List[int]] = None
    exchange: Optional[int] = None
    id: Optional[str] = None
    price: Optional[float] = None
    sequence_number: Optional[int] = None
    sip_timestamp: Optional[int] = None
    participant_timestamp: Optional[int] = None
    size: Optional[float] = None
    tape: Optional[int] = None
    trf_id: Optional[int] = None
    trf_timestamp: Optional[int] = None
    correction: Optional[int] = None


class StockLastTrade(LastTrade):
    """Compact last-trade payload for stock symbols."""


class StockQuote(CuteBase):
    ask_exchange: Optional[int] = None
    ask_price: Optional[float] = None
    ask_size: Optional[float] = None
    bid_exchange: Optional[int] = None
    bid_price: Optional[float] = None
    bid_size: Optional[float] = None
    sequence_number: Optional[int] = None
    sip_timestamp: Optional[int] = None
    tape: Optional[int] = None

    @property
    def midpoint(self) -> Optional[float]:
        if self.bid_price is None or self.ask_price is None:
            return None
        return (self.bid_price + self.ask_price) / 2.0


class StockLastQuote(CuteBase):
    T: Optional[str] = None
    P: Optional[float] = None
    S: Optional[float] = None
    p: Optional[float] = None
    s: Optional[float] = None
    t: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    q: Optional[int] = None
    z: Optional[int] = None

    @property
    def ticker(self) -> Optional[str]:
        return self.T

    @property
    def ask_price(self) -> Optional[float]:
        return self.P

    @property
    def ask_size(self) -> Optional[float]:
        return self.S

    @property
    def bid_price(self) -> Optional[float]:
        return self.p

    @property
    def bid_size(self) -> Optional[float]:
        return self.s

    @property
    def sip_timestamp(self) -> Optional[int]:
        return self.t

    @property
    def bid_exchange(self) -> Optional[int]:
        return self.x

    @property
    def ask_exchange(self) -> Optional[int]:
        return self.y

    @property
    def sequence_number(self) -> Optional[int]:
        return self.q

    @property
    def tape(self) -> Optional[int]:
        return self.z


class StockAggregate(Aggregate):
    """OHLC stock aggregate row."""


class StockOpenClose(OpenClose):
    """Daily stock open-close payload."""


class StockGroupedDaily(CuteBase):
    T: Optional[str] = None
    o: Optional[float] = None
    h: Optional[float] = None
    l: Optional[float] = None
    c: Optional[float] = None
    v: Optional[float] = None
    vw: Optional[float] = None
    t: Optional[int] = None
    n: Optional[int] = None
    otc: Optional[bool] = None

    @property
    def ticker(self) -> Optional[str]:
        return self.T


class StockDeleteResponse(CuteBase):
    status_code: int = Field(default=204)


__all__ = [
    "StockSnapshot",
    "StockSnapshotResponse",
    "StockTicker",
    "StockTickerType",
    "StockRelatedTicker",
    "StockTrade",
    "StockLastTrade",
    "StockQuote",
    "StockLastQuote",
    "StockAggregate",
    "StockOpenClose",
    "StockGroupedDaily",
    "StockDeleteResponse",
]
