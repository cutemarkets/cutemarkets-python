"""``/v1/status/`` resource — unauthenticated system health check."""

from __future__ import annotations

from .._transport import AsyncTransport, Transport
from ..models.common import SystemStatus

_PATH = "/v1/status/"


class StatusResource:
    """Sync system-status resource."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def __call__(self) -> SystemStatus:
        """Poll the health endpoint. Does not require an API key."""
        response = self._t.request("GET", _PATH, require_auth=False)
        return SystemStatus.model_validate(response.data)


class AsyncStatusResource:
    """Async system-status resource."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def __call__(self) -> SystemStatus:
        response = await self._t.request("GET", _PATH, require_auth=False)
        return SystemStatus.model_validate(response.data)


__all__ = ["StatusResource", "AsyncStatusResource"]
