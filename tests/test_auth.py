"""Auth resolution and the Authorization header on the wire."""

from __future__ import annotations

import pytest

from cutemarkets import CuteMarkets
from cutemarkets.errors import ConfigurationError


def test_explicit_api_key_wins_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUTEMARKETS_API_KEY", "cm_env")
    client = CuteMarkets(api_key="cm_explicit")
    assert client.api_key == "cm_explicit"


def test_env_var_used_when_no_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUTEMARKETS_API_KEY", "cm_env_value")
    client = CuteMarkets()
    assert client.api_key == "cm_env_value"


def test_set_api_key_updates_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CUTEMARKETS_API_KEY", raising=False)
    client = CuteMarkets()
    assert client.api_key is None
    client.set_api_key("cm_new")
    assert client.api_key == "cm_new"


def test_authenticated_call_without_key_raises(
    monkeypatch: pytest.MonkeyPatch,
    make_client,
) -> None:
    monkeypatch.delenv("CUTEMARKETS_API_KEY", raising=False)
    client = make_client({}, api_key=None)
    with pytest.raises(ConfigurationError):
        client.tickers.expirations("NFLX")


def test_authorization_header_on_wire(make_client, recorder) -> None:
    client = make_client(
        {
            "/v1/tickers/expirations/NFLX/": {
                "status": "OK",
                "request_id": "cm_x",
                "ticker": "NFLX",
                "results": ["2026-04-02"],
            },
        },
        api_key="cm_abc123",
    )
    client.tickers.expirations("NFLX")
    assert recorder.last_auth == "Bearer cm_abc123"


def test_status_endpoint_does_not_require_key(
    monkeypatch: pytest.MonkeyPatch,
    make_client,
    recorder,
) -> None:
    monkeypatch.delenv("CUTEMARKETS_API_KEY", raising=False)
    client = make_client(
        {
            "/v1/status/": {
                "status": "ok",
                "request_id": "cm_s",
                "services": {"api": {"status": "ok"}},
            }
        },
        api_key=None,
    )
    result = client.status()
    assert result.is_ok
    assert recorder.last_auth is None
