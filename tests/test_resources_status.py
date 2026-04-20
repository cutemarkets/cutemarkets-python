"""Resource test: ``client.status()``."""

from __future__ import annotations


def test_status_parses_services(make_client) -> None:
    payload = {
        "status": "ok",
        "request_id": "cm_status",
        "services": {
            "api": {"status": "ok"},
            "database": {"status": "ok", "latency_ms": 1.42},
            "cache": {"status": "ok", "latency_ms": 0.87},
        },
    }
    client = make_client({"/v1/status/": payload})
    result = client.status()
    assert result.status == "ok"
    assert result.is_ok
    assert result.services["database"].latency_ms == 1.42
    assert result.raw == payload
