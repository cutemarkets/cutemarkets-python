"""Shared test fixtures.

All network I/O is intercepted with :class:`httpx.MockTransport` so the suite
never makes real HTTP calls. Each test registers a handler that inspects the
incoming :class:`httpx.Request` and returns a canned :class:`httpx.Response`.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx
import pytest

from cutemarkets import AsyncCuteMarkets, CuteMarkets

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "X-RateLimit-Plan": "Developer",
    "X-RateLimit-Limit-Minute": "unlimited",
    "X-RateLimit-Remaining-Minute": "9999",
    "X-RateLimit-Limit-Day": "unlimited",
    "X-RateLimit-Remaining-Day": "100000",
}


class RequestRecorder:
    """Captures every request the transport handles, for assertions."""

    def __init__(self) -> None:
        self.requests: List[httpx.Request] = []

    def record(self, request: httpx.Request) -> None:
        self.requests.append(request)

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    @property
    def last_params(self) -> List[Tuple[str, str]]:
        return list(self.last.url.params.multi_items())

    @property
    def last_auth(self) -> Optional[str]:
        return self.last.headers.get("Authorization")


def _make_handler(
    response_map: Dict[str, Any],
    recorder: RequestRecorder,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
) -> Callable[[httpx.Request], httpx.Response]:
    """Return a mock handler that looks up the response by request path."""
    combined_headers = {**DEFAULT_HEADERS, **(headers or {})}

    def handler(request: httpx.Request) -> httpx.Response:
        recorder.record(request)
        path = request.url.path
        body = response_map.get(path)
        if body is None:
            body = response_map.get("__default__")
        if body is None:
            return httpx.Response(
                status_code=404,
                headers=combined_headers,
                content=json.dumps(
                    {
                        "status": "ERROR",
                        "request_id": "cm_missing",
                        "error": {"code": "not_found", "message": f"no fixture for {path}"},
                    }
                ).encode("utf-8"),
            )
        if isinstance(body, tuple):
            status_override, payload = body
            return httpx.Response(
                status_code=status_override,
                headers=combined_headers,
                content=json.dumps(payload).encode("utf-8"),
            )
        return httpx.Response(
            status_code=status_code,
            headers=combined_headers,
            content=json.dumps(body).encode("utf-8"),
        )

    return handler


@pytest.fixture
def recorder() -> RequestRecorder:
    return RequestRecorder()


@pytest.fixture
def make_client(recorder: RequestRecorder):
    def factory(
        response_map: Dict[str, Any],
        *,
        api_key: Optional[str] = "cm_test",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> CuteMarkets:
        handler = _make_handler(response_map, recorder, status_code, headers)
        transport = httpx.MockTransport(handler)
        return CuteMarkets(
            api_key=api_key,
            transport=transport,
            max_retries=0,
        )

    return factory


@pytest.fixture
def make_async_client(recorder: RequestRecorder):
    def factory(
        response_map: Dict[str, Any],
        *,
        api_key: Optional[str] = "cm_test",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncCuteMarkets:
        handler = _make_handler(response_map, recorder, status_code, headers)
        transport = httpx.MockTransport(handler)
        return AsyncCuteMarkets(
            api_key=api_key,
            transport=transport,
            max_retries=0,
        )

    return factory
