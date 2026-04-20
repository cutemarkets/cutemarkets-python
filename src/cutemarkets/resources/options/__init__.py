"""``client.options`` namespace — options market-data resources.

This package wires the individual option-data resources (chain, snapshot,
contracts, trades, quotes, aggs + open-close, indicators) onto a single
:class:`OptionsResource` attached to :attr:`cutemarkets.CuteMarkets.options`.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, AsyncIterator, Iterator, Optional, Union

from ..._pagination import AsyncPage, Page
from ..._transport import AsyncTransport, Transport
from ...models.options import ContractSnapshot, OpenClose
from .aggs import AggsResource, AsyncAggsResource
from .chain import AsyncChainResource, ChainResource
from .contracts import AsyncContractsResource, ContractsResource
from .indicators import AsyncIndicatorsResource, IndicatorsResource
from .quotes import AsyncQuotesResource, QuotesResource
from .snapshot import AsyncSnapshotResource, SnapshotResource
from .trades import AsyncTradesResource, TradesResource

_DateLike = Union[str, _dt.date, _dt.datetime]


class OptionsResource:
    """Sync ``client.options`` namespace."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport
        self._chain = ChainResource(transport)
        self._snapshot = SnapshotResource(transport)
        self.contracts = ContractsResource(transport)
        self.trades = TradesResource(transport)
        self.quotes = QuotesResource(transport)
        self.aggs = AggsResource(transport)
        self.indicators = IndicatorsResource(transport)

    def chain(self, ticker: str, **filters: Any) -> Page[ContractSnapshot]:
        """Fetch one page of the option chain for ``ticker``."""
        return self._chain(ticker, **filters)

    def iter_chain(self, ticker: str, **filters: Any) -> Iterator[ContractSnapshot]:
        """Auto-paginate the option chain for ``ticker``."""
        return self._chain.iter(ticker, **filters)

    def snapshot(self, underlying: str, option_contract: str) -> ContractSnapshot:
        """One-contract snapshot for ``underlying`` / ``option_contract``."""
        return self._snapshot(underlying, option_contract)

    def open_close(
        self,
        ticker: str,
        date: _DateLike,
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> OpenClose:
        """Alias for ``client.options.aggs.open_close(...)``."""
        return self.aggs.open_close(ticker, date, adjusted=adjusted, **extra)


class AsyncOptionsResource:
    """Async ``client.options`` namespace."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport
        self._chain = AsyncChainResource(transport)
        self._snapshot = AsyncSnapshotResource(transport)
        self.contracts = AsyncContractsResource(transport)
        self.trades = AsyncTradesResource(transport)
        self.quotes = AsyncQuotesResource(transport)
        self.aggs = AsyncAggsResource(transport)
        self.indicators = AsyncIndicatorsResource(transport)

    async def chain(self, ticker: str, **filters: Any) -> AsyncPage[ContractSnapshot]:
        return await self._chain(ticker, **filters)

    def iter_chain(self, ticker: str, **filters: Any) -> AsyncIterator[ContractSnapshot]:
        return self._chain.iter(ticker, **filters)

    async def snapshot(self, underlying: str, option_contract: str) -> ContractSnapshot:
        return await self._snapshot(underlying, option_contract)

    async def open_close(
        self,
        ticker: str,
        date: _DateLike,
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> OpenClose:
        return await self.aggs.open_close(ticker, date, adjusted=adjusted, **extra)


__all__ = ["OptionsResource", "AsyncOptionsResource"]
