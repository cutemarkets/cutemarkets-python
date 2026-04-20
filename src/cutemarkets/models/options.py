"""Response models for ``/v1/options/...`` endpoints."""

# ruff: noqa: E741

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import Field

from ._base import CuteBase


class ContractDetails(CuteBase):
    """``details`` block embedded in chain and snapshot responses."""

    ticker: Optional[str] = None
    contract_type: Optional[str] = None
    exercise_style: Optional[str] = None
    expiration_date: Optional[str] = None
    strike_price: Optional[float] = None
    shares_per_contract: Optional[int] = None


class Greeks(CuteBase):
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None


class DayBar(CuteBase):
    """Latest daily bar embedded in chain/snapshot responses."""

    change: Optional[float] = None
    change_percent: Optional[float] = None
    close: Optional[float] = None
    high: Optional[float] = None
    last_updated: Optional[int] = None
    low: Optional[float] = None
    open: Optional[float] = None
    previous_close: Optional[float] = None
    volume: Optional[float] = None
    vwap: Optional[float] = None


class LastQuote(CuteBase):
    """Latest NBBO quote embedded in chain/snapshot responses."""

    ask: Optional[float] = None
    ask_size: Optional[float] = None
    ask_exchange: Optional[int] = None
    bid: Optional[float] = None
    bid_size: Optional[float] = None
    bid_exchange: Optional[int] = None
    last_updated: Optional[int] = None
    midpoint: Optional[float] = None
    timeframe: Optional[str] = None


class EmbeddedLastTrade(CuteBase):
    """``last_trade`` block on chain / snapshot (full field names)."""

    sip_timestamp: Optional[int] = None
    conditions: Optional[List[int]] = None
    price: Optional[float] = None
    size: Optional[float] = None
    exchange: Optional[int] = None
    timeframe: Optional[str] = None


class UnderlyingAsset(CuteBase):
    change_to_break_even: Optional[float] = None
    last_updated: Optional[int] = None
    price: Optional[float] = None
    ticker: Optional[str] = None
    timeframe: Optional[str] = None


class ContractSnapshot(CuteBase):
    """A single option contract snapshot.

    Used both as the ``results`` entry in an option chain (array of
    snapshots) and as the top-level ``results`` object in the single-contract
    snapshot endpoint.
    """

    break_even_price: Optional[float] = None
    day: Optional[DayBar] = None
    details: Optional[ContractDetails] = None
    greeks: Optional[Greeks] = None
    implied_volatility: Optional[float] = None
    last_quote: Optional[LastQuote] = None
    last_trade: Optional[EmbeddedLastTrade] = None
    open_interest: Optional[float] = None
    underlying_asset: Optional[UnderlyingAsset] = None
    fmv: Optional[float] = None
    fmv_last_updated: Optional[int] = None


class Contract(CuteBase):
    """Reference record returned by the contracts endpoints."""

    ticker: Optional[str] = None
    underlying_ticker: Optional[str] = None
    contract_type: Optional[str] = None
    exercise_style: Optional[str] = None
    expiration_date: Optional[str] = None
    strike_price: Optional[float] = None
    shares_per_contract: Optional[int] = None
    primary_exchange: Optional[str] = None
    cfi: Optional[str] = None
    correction: Optional[int] = None
    additional_underlyings: Optional[List[Any]] = None


class Trade(CuteBase):
    """A single historical trade returned by ``/v1/options/trades/{ticker}``."""

    sip_timestamp: Optional[int] = None
    participant_timestamp: Optional[int] = None
    price: Optional[float] = None
    size: Optional[float] = None
    exchange: Optional[int] = None
    conditions: Optional[List[int]] = None
    correction: Optional[int] = None
    id: Optional[str] = None
    sequence_number: Optional[int] = None
    decimal_size: Optional[str] = None


class LastTrade(CuteBase):
    """Compact last-trade payload.

    The live API uses abbreviated keys, and this model keeps them as the
    primary fields (``T``, ``p``, ``s``, ...). Readable property aliases
    (``ticker``, ``price``, ``size``, ...) are provided for convenience.
    """

    T: Optional[str] = None
    p: Optional[float] = None
    s: Optional[float] = None
    t: Optional[int] = None
    x: Optional[int] = None
    c: Optional[List[int]] = None
    y: Optional[int] = None
    f: Optional[int] = None
    r: Optional[int] = None
    i: Optional[str] = None
    q: Optional[int] = None
    e: Optional[int] = None
    z: Optional[int] = None
    ds: Optional[str] = None

    @property
    def ticker(self) -> Optional[str]:
        return self.T

    @property
    def price(self) -> Optional[float]:
        return self.p

    @property
    def size(self) -> Optional[float]:
        return self.s

    @property
    def sip_timestamp(self) -> Optional[int]:
        return self.t

    @property
    def exchange(self) -> Optional[int]:
        return self.x

    @property
    def conditions(self) -> Optional[List[int]]:
        return self.c

    @property
    def participant_timestamp(self) -> Optional[int]:
        return self.y

    @property
    def trf_timestamp(self) -> Optional[int]:
        return self.f

    @property
    def trf_id(self) -> Optional[int]:
        return self.r

    @property
    def trade_id(self) -> Optional[str]:
        return self.i

    @property
    def sequence_number(self) -> Optional[int]:
        return self.q

    @property
    def correction(self) -> Optional[int]:
        return self.e

    @property
    def tape(self) -> Optional[int]:
        return self.z

    @property
    def decimal_size(self) -> Optional[str]:
        return self.ds


class Quote(CuteBase):
    """Historical NBBO-style quote (Expert Plan only)."""

    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    bid_exchange: Optional[int] = None
    ask_exchange: Optional[int] = None
    sequence_number: Optional[int] = None
    sip_timestamp: Optional[int] = None


class Aggregate(CuteBase):
    """OHLC bar for aggregates (custom range and previous day).

    The wire format uses abbreviated single-letter keys. This model keeps
    those as the primary fields and exposes readable property aliases.
    """

    o: Optional[float] = None
    h: Optional[float] = None
    l: Optional[float] = None
    c: Optional[float] = None
    v: Optional[float] = None
    vw: Optional[float] = None
    t: Optional[int] = None
    n: Optional[int] = None
    T: Optional[str] = None

    @property
    def open(self) -> Optional[float]:
        return self.o

    @property
    def high(self) -> Optional[float]:
        return self.h

    @property
    def low(self) -> Optional[float]:
        return self.l

    @property
    def close(self) -> Optional[float]:
        return self.c

    @property
    def volume(self) -> Optional[float]:
        return self.v

    @property
    def vwap(self) -> Optional[float]:
        return self.vw

    @property
    def timestamp(self) -> Optional[int]:
        return self.t

    @property
    def trade_count(self) -> Optional[int]:
        return self.n

    @property
    def ticker(self) -> Optional[str]:
        return self.T


class OpenClose(CuteBase):
    """Flat daily open/close payload from ``/v1/options/open-close/``.

    This endpoint does not use the standard envelope: ``results`` is absent
    and every field (``symbol``, ``open``, ``close``, ...) sits at the top
    level.

    ``from`` is a reserved keyword in Python, so we expose it as
    :attr:`from_date`. ``preMarket`` / ``afterHours`` keep their wire names
    and also expose snake_case property aliases.
    """

    status: Optional[str] = None
    request_id: Optional[str] = None
    symbol: Optional[str] = None
    from_date: Optional[str] = Field(default=None, alias="from")
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    preMarket: Optional[float] = None
    afterHours: Optional[float] = None
    otc: Optional[bool] = None
    adjusted: Optional[bool] = None

    @property
    def pre_market(self) -> Optional[float]:
        return self.preMarket

    @property
    def after_hours(self) -> Optional[float]:
        return self.afterHours


__all__ = [
    "ContractDetails",
    "Greeks",
    "DayBar",
    "LastQuote",
    "EmbeddedLastTrade",
    "UnderlyingAsset",
    "ContractSnapshot",
    "Contract",
    "Trade",
    "LastTrade",
    "Quote",
    "Aggregate",
    "OpenClose",
]
