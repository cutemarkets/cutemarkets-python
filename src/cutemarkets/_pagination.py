"""Pagination helpers: :class:`Page`, :class:`AsyncPage`, and iterators.

Every paginated list endpoint returns a :class:`Page` from the one-shot
``list(...)`` methods and yields individual items from the ``iter_list(...)``
generators. Pages hold the parsed results, the ``next_url`` (when present),
the ``request_id``, and the :class:`RateLimitInfo` parsed from response
headers.

Pagination strictly follows the ``next_url`` field returned by the server:
the URL is requested verbatim with the same ``Authorization`` header rather
than being reconstructed client-side.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
)

from ._transport import AsyncTransport, Response, Transport
from .models.common import RateLimitInfo

T = TypeVar("T")


def _parse_page(
    response: Response,
    parser: Callable[[Any], T],
) -> "_PageState[T]":
    data = response.data if isinstance(response.data, dict) else {}
    raw_results = data.get("results") or []
    if not isinstance(raw_results, list):
        raw_results = [raw_results]
    return _PageState(
        results=[parser(item) for item in raw_results],
        next_url=data.get("next_url") if isinstance(data.get("next_url"), str) else None,
        request_id=response.request_id,
        rate_limit=response.rate_limit,
        status=data.get("status") if isinstance(data.get("status"), str) else None,
    )


@dataclass
class _PageState(Generic[T]):
    results: List[T]
    next_url: Optional[str]
    request_id: Optional[str]
    rate_limit: RateLimitInfo
    status: Optional[str]


@dataclass
class Page(Generic[T]):
    """A single page of results from a list endpoint (sync).

    Attributes:
        results: The parsed rows for this page.
        next_url: Full URL for the next page, or ``None`` if this is the last.
        request_id: CuteMarkets ``request_id`` for the underlying HTTP call.
        rate_limit: :class:`RateLimitInfo` parsed from response headers.
        status: The raw ``status`` field from the response envelope.

    Call :meth:`next` to fetch the following page; call :meth:`iter_all` to
    lazily walk every remaining page.
    """

    results: List[T] = field(default_factory=list)
    next_url: Optional[str] = None
    request_id: Optional[str] = None
    rate_limit: RateLimitInfo = field(default_factory=RateLimitInfo)
    status: Optional[str] = None
    _transport: Optional[Transport] = None
    _parser: Optional[Callable[[Any], T]] = None

    @classmethod
    def from_response(
        cls,
        response: Response,
        *,
        transport: Transport,
        parser: Callable[[Any], T],
    ) -> "Page[T]":
        state = _parse_page(response, parser)
        return cls(
            results=state.results,
            next_url=state.next_url,
            request_id=state.request_id,
            rate_limit=state.rate_limit,
            status=state.status,
            _transport=transport,
            _parser=parser,
        )

    @property
    def has_next(self) -> bool:
        return bool(self.next_url)

    def next(self) -> Optional["Page[T]"]:
        """Fetch the next page by following ``next_url`` verbatim.

        Returns ``None`` when the current page is the last one.
        """
        if not self.next_url or self._transport is None or self._parser is None:
            return None
        response = self._transport.request_url("GET", self.next_url)
        return Page.from_response(response, transport=self._transport, parser=self._parser)

    def iter_all(self) -> Iterator[T]:
        """Yield items from this page, then from every subsequent page."""
        yield from self.results
        page: Optional[Page[T]] = self.next()
        while page is not None:
            yield from page.results
            page = page.next()

    def __iter__(self) -> Iterator[T]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)


@dataclass
class AsyncPage(Generic[T]):
    """A single page of results from a list endpoint (async)."""

    results: List[T] = field(default_factory=list)
    next_url: Optional[str] = None
    request_id: Optional[str] = None
    rate_limit: RateLimitInfo = field(default_factory=RateLimitInfo)
    status: Optional[str] = None
    _transport: Optional[AsyncTransport] = None
    _parser: Optional[Callable[[Any], T]] = None

    @classmethod
    def from_response(
        cls,
        response: Response,
        *,
        transport: AsyncTransport,
        parser: Callable[[Any], T],
    ) -> "AsyncPage[T]":
        state = _parse_page(response, parser)
        return cls(
            results=state.results,
            next_url=state.next_url,
            request_id=state.request_id,
            rate_limit=state.rate_limit,
            status=state.status,
            _transport=transport,
            _parser=parser,
        )

    @property
    def has_next(self) -> bool:
        return bool(self.next_url)

    async def next(self) -> Optional["AsyncPage[T]"]:
        if not self.next_url or self._transport is None or self._parser is None:
            return None
        response = await self._transport.request_url("GET", self.next_url)
        return AsyncPage.from_response(
            response,
            transport=self._transport,
            parser=self._parser,
        )

    async def iter_all(self) -> AsyncIterator[T]:
        for item in self.results:
            yield item
        page: Optional[AsyncPage[T]] = await self.next()
        while page is not None:
            for item in page.results:
                yield item
            page = await page.next()

    def __iter__(self) -> Iterator[T]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)


def iter_pages(page: Page[T]) -> Iterator[T]:
    """Module-level convenience: yield every item across every page (sync)."""
    yield from page.iter_all()


async def aiter_pages(page: AsyncPage[T]) -> AsyncIterator[T]:
    """Module-level convenience: yield every item across every page (async)."""
    async for item in page.iter_all():
        yield item


__all__ = ["Page", "AsyncPage", "iter_pages", "aiter_pages"]
