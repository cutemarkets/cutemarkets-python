"""Response models for ``/v1/tickers/...`` endpoints."""

from __future__ import annotations

from typing import List, Optional

from ._base import CuteBase


class TickerSearchResult(CuteBase):
    """One row in :meth:`~cutemarkets.CuteMarkets.tickers.search`."""

    symbol: Optional[str] = None
    name: Optional[str] = None


class ExpirationsResponse(CuteBase):
    """Response shape for ``/v1/tickers/expirations/{ticker}``.

    The envelope for this endpoint is slightly different: it includes a
    top-level ``ticker`` field alongside ``results`` (a list of ``YYYY-MM-DD``
    strings).
    """

    status: Optional[str] = None
    request_id: Optional[str] = None
    ticker: Optional[str] = None
    results: List[str] = []


__all__ = ["TickerSearchResult", "ExpirationsResponse"]
