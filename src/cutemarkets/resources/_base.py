"""Base classes for sync and async resources."""

from __future__ import annotations

import urllib.parse
from typing import Any, Callable, TypeVar

from .._transport import AsyncTransport, Transport

T = TypeVar("T")


def quote_path(value: str) -> str:
    """URL-encode a path segment, preserving ``:`` for OCC tickers.

    Options tickers like ``O:NFLX260402C00075000`` contain a colon, which is
    a reserved character in URLs and should be percent-encoded by strict
    clients. CuteMarkets accepts both forms, so we keep the colon literal in
    the rendered path to match the examples in the docs.
    """
    return urllib.parse.quote(value, safe=":")


class _ResourceBase:
    def __init__(self, transport: Transport) -> None:
        self._t = transport


class _AsyncResourceBase:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport


def _parse_single(data: Any, parser: Callable[[Any], T]) -> T:
    """Pull ``results`` out of an envelope and parse it, falling back to the
    raw payload when no ``results`` key is present (e.g. ``open-close``)."""
    if isinstance(data, dict) and "results" in data:
        return parser(data["results"])
    return parser(data)


__all__ = ["quote_path", "_ResourceBase", "_AsyncResourceBase", "_parse_single"]
