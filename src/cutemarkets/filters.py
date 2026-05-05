"""Typed filter dictionaries for the most-used list endpoints."""

from __future__ import annotations

import datetime as dt
from typing import Literal, Union

from typing_extensions import TypedDict

DateLike = Union[str, dt.date, dt.datetime]


class PaginationFilters(TypedDict, total=False):
    limit: int
    page: str
    sort: str
    order: Literal["asc", "desc"]


class ChainFilters(PaginationFilters, total=False):
    as_of: DateLike
    contract_type: Literal["call", "put"]
    expiration_date: DateLike
    expiration_date_gte: DateLike
    expiration_date_gt: DateLike
    expiration_date_lte: DateLike
    expiration_date_lt: DateLike
    strike_price: float
    strike_price_gte: float
    strike_price_gt: float
    strike_price_lte: float
    strike_price_lt: float


class ContractFilters(PaginationFilters, total=False):
    as_of: DateLike
    underlying_ticker: str
    contract_type: Literal["call", "put"]
    expiration_date: DateLike
    expiration_date_gte: DateLike
    expiration_date_gt: DateLike
    expiration_date_lte: DateLike
    expiration_date_lt: DateLike
    strike_price: float
    strike_price_gte: float
    strike_price_gt: float
    strike_price_lte: float
    strike_price_lt: float


class QuoteFilters(PaginationFilters, total=False):
    timestamp: DateLike
    timestamp_gte: DateLike
    timestamp_gt: DateLike
    timestamp_lte: DateLike
    timestamp_lt: DateLike
    sort: Literal["timestamp"]


class TradeFilters(PaginationFilters, total=False):
    timestamp: DateLike
    timestamp_gte: DateLike
    timestamp_gt: DateLike
    timestamp_lte: DateLike
    timestamp_lt: DateLike
    sort: Literal["timestamp"]


__all__ = [
    "ChainFilters",
    "ContractFilters",
    "QuoteFilters",
    "TradeFilters",
]
