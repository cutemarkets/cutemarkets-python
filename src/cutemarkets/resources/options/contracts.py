"""``/v1/options/contracts/`` — reference contracts (list + detail)."""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator, Optional

from ..._pagination import AsyncPage, Page
from ..._transport import AsyncTransport, Transport
from ...models.options import Contract
from .._base import _parse_single, quote_path


def _detail_path(options_ticker: str) -> str:
    return f"/v1/options/contracts/{quote_path(options_ticker)}/"


_LIST_PATH = "/v1/options/contracts/"


class ContractsResource:
    """Sync contracts resource.

    See [docs/contracts.md](https://cutemarkets.com/docs/contracts).
    """

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def list(self, **filters: Any) -> Page[Contract]:
        """List reference contracts. Supports range filters via ``_gte``/``_gt``/``_lte``/``_lt``."""
        response = self._t.request("GET", _LIST_PATH, params=filters)
        return Page.from_response(response, transport=self._t, parser=Contract.model_validate)

    def iter_list(self, **filters: Any) -> Iterator[Contract]:
        """Auto-paginate :meth:`list`, yielding one contract at a time."""
        page = self.list(**filters)
        yield from page.iter_all()

    def get(self, options_ticker: str, *, as_of: Optional[Any] = None) -> Contract:
        """Return detail for one contract by its options ticker."""
        response = self._t.request(
            "GET",
            _detail_path(options_ticker),
            params={"as_of": as_of},
        )
        return _parse_single(response.data, Contract.model_validate)


class AsyncContractsResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def list(self, **filters: Any) -> AsyncPage[Contract]:
        response = await self._t.request("GET", _LIST_PATH, params=filters)
        return AsyncPage.from_response(
            response, transport=self._t, parser=Contract.model_validate
        )

    async def iter_list(self, **filters: Any) -> AsyncIterator[Contract]:
        page = await self.list(**filters)
        async for item in page.iter_all():
            yield item

    async def get(self, options_ticker: str, *, as_of: Optional[Any] = None) -> Contract:
        response = await self._t.request(
            "GET",
            _detail_path(options_ticker),
            params={"as_of": as_of},
        )
        return _parse_single(response.data, Contract.model_validate)


__all__ = ["ContractsResource", "AsyncContractsResource"]
