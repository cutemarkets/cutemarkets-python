"""Common response types: rate-limit info and system status."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from pydantic import BaseModel, ConfigDict

from ._base import CuteBase


class RateLimitInfo(BaseModel):
    """Rate-limit state parsed from response headers.

    ``limit_minute`` and ``limit_day`` are strings because the API returns
    ``"unlimited"`` for paid plans. Numeric values are coerced to ``int`` when
    possible.
    """

    model_config = ConfigDict(extra="allow")

    plan: Optional[str] = None
    limit_minute: Optional[str] = None
    remaining_minute: Optional[int] = None
    limit_day: Optional[str] = None
    remaining_day: Optional[int] = None

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> "RateLimitInfo":
        def _int(value: Optional[str]) -> Optional[int]:
            if value is None:
                return None
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        return cls(
            plan=headers.get("X-RateLimit-Plan") or headers.get("x-ratelimit-plan"),
            limit_minute=headers.get("X-RateLimit-Limit-Minute")
            or headers.get("x-ratelimit-limit-minute"),
            remaining_minute=_int(
                headers.get("X-RateLimit-Remaining-Minute")
                or headers.get("x-ratelimit-remaining-minute")
            ),
            limit_day=headers.get("X-RateLimit-Limit-Day")
            or headers.get("x-ratelimit-limit-day"),
            remaining_day=_int(
                headers.get("X-RateLimit-Remaining-Day")
                or headers.get("x-ratelimit-remaining-day")
            ),
        )


class ServiceStatus(CuteBase):
    """Sub-service health reported under :attr:`SystemStatus.services`."""

    status: Optional[str] = None
    latency_ms: Optional[float] = None


class SystemStatus(CuteBase):
    """Response shape for :meth:`cutemarkets.CuteMarkets.status`.

    ``status`` is ``"ok"`` when every service is nominal, or ``"degraded"``
    when one or more services are impacted.
    """

    status: Optional[str] = None
    request_id: Optional[str] = None
    services: Dict[str, ServiceStatus] = {}

    @property
    def is_ok(self) -> bool:
        """True when the top-level status is exactly ``"ok"``."""
        return (self.status or "").lower() == "ok"


__all__ = ["RateLimitInfo", "ServiceStatus", "SystemStatus"]
