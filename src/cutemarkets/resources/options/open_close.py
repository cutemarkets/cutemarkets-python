"""``/v1/options/open-close/{ticker}/{date}/`` — daily open/close snapshot.

This endpoint does not use the standard envelope: the payload is flat, so
we parse it directly into :class:`~cutemarkets.models.options.OpenClose`.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Optional, Union

from ..._transport import AsyncTransport, Transport
from ...models.options import OpenClose
from .._base import quote_path


def _coerce_date(value: Union[str, _dt.date, _dt.datetime]) -> str:
    if isinstance(value, _dt.datetime):
        return value.date().isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    return str(value)


def _path(ticker: str, date: Union[str, _dt.date, _dt.datetime]) -> str:
    return f"/v1/options/open-close/{quote_path(ticker)}/{_coerce_date(date)}/"


class OpenCloseResource:
    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def __call__(
        self,
        ticker: str,
        date: Union[str, _dt.date, _dt.datetime],
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> OpenClose:
        """Fetch regular-session open/close for one contract on one day.

        See [docs/aggregates.md](https://cutemarkets.com/docs/aggregates).
        """
        params = {"adjusted": adjusted, **extra}
        response = self._t.request("GET", _path(ticker, date), params=params)
        return OpenClose.model_validate(response.data)


class AsyncOpenCloseResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def __call__(
        self,
        ticker: str,
        date: Union[str, _dt.date, _dt.datetime],
        *,
        adjusted: Optional[bool] = None,
        **extra: Any,
    ) -> OpenClose:
        params = {"adjusted": adjusted, **extra}
        response = await self._t.request("GET", _path(ticker, date), params=params)
        return OpenClose.model_validate(response.data)


__all__ = ["OpenCloseResource", "AsyncOpenCloseResource"]
